import React from 'react';

export default class SongInfo extends React.Component {
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

