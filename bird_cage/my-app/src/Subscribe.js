import React, { Component } from 'react';
import logo from './img/canary.png';
import { Col, Button, Form, FormGroup, Label, Input, FormText, Row, CardImg } from 'reactstrap';

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
        <div>
            <Col sm={6}>
            <div>
            <img src = {logo} align="left"/>
            </div>
            <div>
                <p>Air pollution is a big problem in London. After suffering from the affects first hand, I was
                determined to help make life easier for others that might also be suffering from the poor air quality
                of the city. If you find that some days you feel a little short of breath for no reason, or perhaps you
                have had some unexplained chest pain or just a general feeling of being unwell you may be affected by
                air pollution.</p>
            </div>
            <div>

            <Form onSubmit={this.handleSubmit}>
                <FormGroup row>
                    <Label for="phone" sm={2}>Phone</Label>
                    <Col sm={6}>
                        <Input id="phone" name="phone" type="text" placeholder="07719143007"/>
                    </Col>
                </FormGroup>
                <FormGroup row>
                    <Label for="topic" sm={2}>Alert level</Label>
                    <Col sm={6}>
                        <Input type="select" name="topic" id="topic">
                        <option value="green">Hourly alerts</option>
                        <option value="yellow">Highly sensitive</option>
                        <option value="amber">Moderately sensitive</option>
                        <option value="red">No known sensitivity</option>
                        </Input>
                    </Col>
                </FormGroup>
                <Button color="danger" align='right'>Subscribe!</Button>
            </Form>

            </div>
                </Col>
        </div>
    );
  }
}

export default MyForm
