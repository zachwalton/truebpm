import React, { Component } from 'react';
//import Suggest from './Suggest.js';
import Select from 'react-select';

import 'react-select/dist/react-select.css';
import './App.css';

var isLoadingExternally = true;

const getSimfiles = (input) => {
  return fetch(`/api/v1/simfiles`)
    .then((response) => {
      return response.json();
    }).then((json) => {
      return { options: json };
    });
}


class SongInfo extends Component {
  render() {
    return this.props.songInfo ? (
      <div className="App-songinfo">
        {
          this.props.songInfo.result.bpm_list.map(function(message) {
            return <div key={message}>
              {message}
              <br />
            </div>;
          })
        }
        <p className="App-speedsuggestion">{this.props.songInfo.result.suggestion}</p>
        <div className="App-speedwarning">
          {
            this.props.songInfo.result.speed_changes.map(function(message) {
              return <div key={message}>
                {message}
                <br />
              </div>;
            })
          }
        </div>
      </div>
    ) : null;
  }
}

class App extends Component {
  constructor() {
    super();
    this.state = {
      songInfo: null,
    };
    this.fetchSuggestions = this.fetchSuggestions.bind(this);
  }

  fetchSuggestions(song) {
    return fetch(`/api/v1/simfiles/` + song.label + `?style=Single&difficulty=Hard&preferred_rate=570&speed_change_threshold=4`)
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
