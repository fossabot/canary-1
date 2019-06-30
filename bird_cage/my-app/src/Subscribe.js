import React, { Component } from 'react';

class MyForm extends React.Component {
  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();
    const data = new FormData(event.target);

    fetch('/api/subscribe', {
      method: 'POST',
      body: data,
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label htmlFor="phone">Enter your phone number</label>
        <input id="phone" name="phone" type="text" />

        <label htmlFor="topic">Enter your alert level</label>
        <select name="topic" id="topic" type="text">
        <option value="green">Hourly alerts</option>
        <option value="yellow">Highly sensitive</option>
        <option value="amber">Moderately sensitive</option>
        <option value="red">No known sensitivity</option>
        </select>

        <button>Subscribe!</button>
      </form>
    );
  }
}

export default MyForm;
