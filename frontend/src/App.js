import React, { Component } from 'react';
//import Suggest from './Suggest.js';
import Select from 'react-select';
import Slider, {Handle} from 'rc-slider';
import Tooltip from 'rc-tooltip';

import 'react-select/dist/react-select.css';
import 'rc-slider/assets/index.css';

import './App.css';

var isLoadingExternally = true;

const handle = (props) => {
  const { value, dragging, index, ...restProps } = props;
  return (
    <Tooltip
      prefixCls="rc-slider-tooltip"
      overlay={value}
      visible={dragging}
      placement="top"
      key={index}
    >
      <Handle {...restProps} />
    </Tooltip>
  );
};

const getSimfiles = (input) => {
  return fetch(`/api/v1/simfiles`)
    .then((response) => {
      return response.json();
    }).then((json) => {
      return { options: json };
    });
}


class SongInfo extends Component {
  renderStops() {
    return this.props.songInfo.result.stops ? (
      <div>
        <strong>Stops: {this.props.songInfo.result.stops}</strong>
        <br /><br />
      </div>
    ) : null;
  }
  renderSpeedChanges() {
    return this.props.songInfo.result.speed_changes.length ? (
      <div className="App-speedwarning">
        {
          this.props.songInfo.result.speed_changes.map(function(message) {
            return (
              <div key={message}>
                {message}
                <br />
              </div>
            );
          })
        }
      </div>
    ) : null;
  }
  render() {
    return this.props.songInfo ? (
      <div className="App-songinfo">
        {this.renderStops()}
        {
          this.props.songInfo.result.bpm_list.map(function(message) {
            return <div key={message}>
              {message}
              <br />
            </div>;
          })
        }
        <p className="App-speedsuggestion">{this.props.songInfo.result.suggestion}</p>
        {this.renderSpeedChanges()}
      </div>
    ) : null;
  }
}

class App extends Component {
  constructor() {
    super();
    this.state = {
      selectedSong: null,
      songInfo: null,
      preferredReadSpeed: 573,
    };
    this.fetchSuggestions = this.fetchSuggestions.bind(this);
    this.onSliderChange = this.onSliderChange.bind(this);
    this.onSliderSelect = this.onSliderSelect.bind(this);
  }

  onSliderChange(value) {
    this.setState({'preferredReadSpeed': value});
  }

  onSliderSelect(value) {
    if (this.state.selectedSong) {
      this.fetchSuggestions(this.state.selectedSong);
    }
  }

  fetchSuggestions(song) {
    this.setState({'selectedSong': song});
    return fetch(`/api/v1/simfiles/` + song.label + `?style=Single&difficulty=Hard&preferred_rate=` + this.state.preferredReadSpeed + `&speed_change_threshold=4`)
      .then((response) => {
        return response.json();
      }).then(function(info) {
        this.setState({'songInfo': info});
      }.bind(this));
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <h3>true BPM</h3>
        </div>
        <p className="description">
          figure out the actual BPM of a chart on DDR A.
        </p>
        <div className="Content">
          <small><i>preferred read speed:</i></small>
          <Slider
            min={50}
            max={800}
            defaultValue={573}
            value={this.state.preferredReadSpeed}
		    handle={handle}
            step={5}
            onChange={this.onSliderChange}
            onAfterChange={this.onSliderSelect}
          />
          <br />
          <Select.Async
            name="form-field-name"
            value="one"
            loadOptions={getSimfiles}
            isLoading={isLoadingExternally}
            onChange={this.fetchSuggestions}
          />
        </div>
        <SongInfo songInfo={this.state.songInfo} />
      </div>
    );
  }
}

export default App;
