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
        <label htmlFor="phone">Enter phone number</label>
        <input id="phone" name="phone" type="text" />

        <label htmlFor="topic">Enter topic</label>
        <input id="topic" name="topic" type="text" />

        <button>Send data!</button>
      </form>
    );
  }
}

export default MyForm;
