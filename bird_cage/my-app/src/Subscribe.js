import React, { Component } from 'react';
import logo from './img/canary.png';
import { Col, Button, Form, FormGroup, Label, Input, FormText, Row, CardImg, Badge, Container } from 'reactstrap';

const ColoredLine = ({ color }) => (
    <hr
        style={{
            color: color,
            backgroundColor: color,
            height: 50
        }}
    />
);


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
        <Container fluid="true">
            <Row className="mt-1">
                <Col className="center"><img src = {logo}/><Badge color="danger">Beta</Badge></Col>
                <Col className="flex-xs-middle">
                    <h1 className="header-font">
                        <br></br>
                        <p>Chirping Canary</p>
                        <p className="arial">Air Pollution Early Warning System</p>
                    </h1>
                </Col>
            </Row>

            <Row className="mt-1">
                <Col><ColoredLine color="gold" /></Col>
            </Row>

            <Row className="mt-1">
                <Col>
                    <p>
                    Air pollution is a big problem in London.
                    </p>
                    <p>
                    If you find that some days you feel a little short of breath for no reason, or perhaps you
                    have had some unexplained chest pain or just a general feeling of being unwell you may be affected by
                    air pollution.
                    </p>
                    <p>
                    It doesn't have to be this way! With Chirping Canary on your side you don't need to be caught off-guard
                    by a bad pollution day. Like the canary in the coal mine, Chirping Canary is here to warn you when
                    the pollution levels in London reach unacceptable levels.
                    </p>
                    <p>
                    Enter your phone number and select your sensitivity level to air pollution to receive free notifcations
                    every time the air pollution reaches a level that affects you.
                    </p>
                </Col>

                <Col>
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
                </Col>
            </Row>
        </Container>
    );
  }
}

export default MyForm
