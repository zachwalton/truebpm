from collections import OrderedDict
import operator
from StringIO import StringIO

class SMParser(object):

    TOKENS = (
        'TITLE', 'SUBTITLE', 'ARTIST',
        'TITLETRANSLIT', 'SUBTITLETRANSLIT',
        'ARTISTTRANSLIT', 'CREDIT', 'BANNER',
        'BACKGROUND', 'LYRICSPATH', 'CDTITLE',
        'MUSIC', 'OFFSET', 'SAMPLESTART',
        'SAMPLELENGTH', 'SELECTABLE', 'DISPLAYBPM',
        'BPMS', 'STOPS', 'BGCHANGES',
    )

    BOM_CHAR = '\xef\xbb\xbf'

    # https://remywiki.com/DDR_AC_General_Info#SPEED
    VALID_DDR_A_SPEED_MODS = (
        0.25, 0.5, 0.75, 1.0,
        1.25, 1.5, 1.75, 2.0,
        2.25, 2.5, 2.75, 3.0,
        3.25, 3.5, 3.75, 4.0,
        4.5, 5.0, 5.5, 6.0, 6.5,
        7.0, 7.5, 8.0
    )

    SECTION_HEADER = '//--'

    STYLES = ('dance-single', 'dance-double')
    DIFFICULTIES = ('Beginner', 'Easy', 'Medium', 'Hard', 'Challenge')
    FOOT_RATINGS = range(1, 11)
    STEP_TYPES = '0123'

    def __init__(self, simfile):
        self.charts = {}
        self._simfile = simfile
        self._parse_header_tokens()
        self._parse_sections()

    def _parse_header_tokens(self):
        parsing_multiline_value = False
        for line in StringIO(self._simfile):
            try:
                token, value = (line.strip()
                                .replace(self.BOM_CHAR, '')
                                .split(':')[:2])
            except ValueError:
                if not parsing_multiline_value:
                    continue

            if token[1:] in self.TOKENS and not token[1:] in ('BPMS', 'STOPS'):
                setattr(self, token[1:], value.strip(';'))

            if parsing_multiline_value:
                if ';' in line:
                    parsing_multiline_value = False
                    continue

                token, value = (line.strip().strip(',')
                                .replace(self.BOM_CHAR, '')
                                .split('=')[:2])
                self.BPMS[token] = value

            if token[1:] in ('BPMS', 'STOPS'):
                values = [measure.split('=') for measure in value.strip(';').split(',')]
                values = OrderedDict(values) if len(values[0]) > 1 else OrderedDict()
                setattr(self, token[1:], OrderedDict(values))
                if not ';' in value:
                    parsing_multiline_value = True
            elif line.startswith(self.SECTION_HEADER):
                break

    def _parse_sections(self):

        def _dos_to_unix(s):
            return s.replace('\r', '')

        parsing = False
        parsing_measure = False
        measure_counter = 1

        for line in StringIO(self._simfile):
            line = _dos_to_unix(line.strip())

            if not parsing and not line.startswith(self.SECTION_HEADER):
                if ':' in line and line.split(':')[0] in self.STYLES:
                    # handle badly-behaved simfiles with no section headers
                    parsing = True
                    style = 'Double' if 'double' in line else 'Single'
                    self.charts[style] = self.charts.setdefault(style, {})
                continue

            elif line.startswith(self.SECTION_HEADER):
                # parse section header
                parsing = True
                style = 'Double' if 'double' in line else 'Single'
                self.charts[style] = self.charts.setdefault(style, {})

            elif parsing and ':' in line:
                # Parse #INFO section
                value = line.split(':')[0]
                if value in self.DIFFICULTIES:
                    difficulty = value
                    self.charts[style][difficulty] = {}
                elif value in self.FOOT_RATINGS:
                    self.charts[style][difficulty]['foot rating'] = value
                elif ',' in value:
                    self.charts[style][difficulty]['?'] = value

            elif all((c in self.STEP_TYPES for c in line)) and line != '':
                # parse individual measures
                if parsing_measure:
                    measure['steps'].append(line)
                else:
                    measure = {'measure': measure_counter, 'steps': [line]}
                    parsing_measure = True
                self.charts[style][difficulty]['chart'] = self.charts[style][
                    difficulty].setdefault('chart', [])

            elif line.startswith(',') and parsing_measure:
                # stop parsing measure
                self.charts[style][difficulty]['chart'].append(measure)
                parsing_measure = False
                measure_counter += 1

            elif line.startswith(';') and parsing:
                # stop parsing section
                if parsing_measure:
                    self.charts[style][difficulty]['chart'].append(measure)
                parsing, parsing_measure = False, False
                measure_counter = 1

    def _float_to_str(self, num):
        if num.is_integer():
            return "%d" % int(num)
        return "%.2f" % num

    def bpm_durations(self, style, difficulty):
        num_measures = len(self.charts[style][difficulty]['chart']) * 4
        last_bpm, last_measure = None, None
        durations = {}

        for measure, bpm in self.BPMS.iteritems():
            if last_bpm is not None:
                durations[last_bpm] = durations.setdefault(last_bpm, 0) + (
                    float(measure) - float(last_measure))
            last_measure = measure
            last_bpm = bpm

        # tack on the remaining measures in the song to the last reported
        # bpm
        durations[last_bpm] = durations.setdefault(last_bpm, 0) + (
            num_measures - sum(durations.values()))

        return num_measures, durations

    def analyze(self, style, difficulty, preferred_rate=None, speed_change_threshold=5):
        num_measures, durations = self.bpm_durations(style, difficulty)
        longest_bpm, longest_duration, other_long_durations = None, 0, {}
        analysis = {
            'bpm_list': [],
            'suggestion': None,
            'speed_changes': [],
            'stops': len(self.STOPS.keys()) if hasattr(self, 'STOPS') else 0,
        }

        for bpm, measures in reversed(sorted(durations.items(),
                                             key=operator.itemgetter(1))):
            longest_duration = measures if measures > longest_duration else longest_duration
            longest_bpm = float(bpm) if longest_bpm is None else longest_bpm
            pct = measures / num_measures * 100

            # if this isn't the BPM with the longest duration and it's greater
            # than 5 percent of the song, call it out.
            if pct > float(speed_change_threshold) and measures < longest_duration:
                other_long_durations[bpm] = measures

            title = self.TITLE
            analysis['bpm_list'].append(
                "{title} is at {bpm} BPM for {measures} measures ({pct:.2f}%)".format(**locals()))

        if preferred_rate:
            mods = self.calculate_speed_mods(longest_bpm, int(preferred_rate))

            analysis['suggestion'] = "Suggested speed mods: {lower_mod} = {lower_bpm}, {upper_mod} = {upper_bpm}".format(
                lower_mod='x%s' % self._float_to_str(mods['lower']['mod']),
                lower_bpm=int(mods['lower']['rate']),
                upper_mod='x%s' % self._float_to_str(mods['upper']['mod']),
                upper_bpm=int(mods['upper']['rate']),
            )

            if other_long_durations:
                for bpm, measures in reversed(sorted(other_long_durations.items(),
                                                     key=operator.itemgetter(1))):
                    analysis['speed_changes'].append(("[BPM change] Suggested mods will result in read speed of "
                           "{lower_outlier_rate} @ {lower_mod} or "
                           "{upper_outlier_rate} @ {upper_mod} for "
                           "{pct:.2f}% of song").format(
                        lower_outlier_rate=(float(bpm) * mods['lower']['mod']),
                        lower_mod='x%s' % self._float_to_str(mods['lower']['mod']),
                        upper_outlier_rate=(float(bpm) * mods['upper']['mod']),
                        upper_mod='x%s' % self._float_to_str(mods['upper']['mod']),
                        pct=measures / num_measures * 100,
                    ))

        return analysis

    def calculate_speed_mods(self, bpm, preferred_rate):
        mods = {
            'lower': {
                'rate': 0,
                'mod': None,
            },
            'upper': {
                'rate': 0,
                'mod': None,
            },
        }
        # Get the speed mod that results in a read speed immediately
        # below and above the preferred speed
        for mod in self.VALID_DDR_A_SPEED_MODS:
            rate = mod * bpm
            if rate > mods['lower']['rate'] and rate <= preferred_rate:
                mods['lower'] = {'rate': rate, 'mod': mod}
            if rate >= preferred_rate:
                mods['upper'] = {'rate': rate, 'mod': mod}
                break

        return mods
