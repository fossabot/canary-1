import React, { Component } from 'react';
import logo from './img/canary.png';
import { Col, Button, Form, FormGroup, Label, Input, FormText, Row, CardImg, Badge, Container } from 'reactstrap';


function Home(props) {
  return (
    <Col>
        <Form onSubmit={props.onClick}>
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
            <Col sm={6}>
            <Button color="danger" align='right'>Subscribe</Button>
            </Col>
            <Col sm={6}>
            <Button color="secondary" align='right'>UnSubscribe</Button>
            </Col>
        </Form>
    </Col>
  );
};


function ConfirmSubscription(props) {
  return (
    <Col>
        <Form onSubmit={props.onClick}>
            <FormGroup row>
                <Label for="verifycode" sm={2}>Verification Code</Label>
                <Col sm={6}>
                    <Input id="verifycode" name="verifycode" type="text" placeholder=""/>
                </Col>
            </FormGroup>
            <Col sm={6}>
            <Button color="danger" align='right'>Confirm Subscription</Button>
            </Col>
        </Form>
    </Col>
  );
};

class Subscribe extends Component {

  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleSubmit2 = this.handleSubmit2.bind(this);
    this.state = {
      flow: 'home'
    };
  };

  handleSubmit(event) {
    event.preventDefault();
    const data = new FormData(event.target);

    fetch('/api/subscribe', {
      method: 'POST',
      body: data,
    });

    this.setState({flow: "confirmsubscription"})
  };

  handleSubmit2(event) {
    event.preventDefault();
    const data = new FormData(event.target);

    fetch('/api/subscribe', {
      method: 'POST',
      body: data,
    });

    this.setState({flow: "confirmsubscription"})
  };

  render() {

    const flow = this.state.flow
    let currentForm

    if (flow == 'home') {
      currentForm = <Home onClick={this.handleSubmit}/>;
    } else if (flow == 'confirmsubscription')  {
      currentForm = <ConfirmSubscription onClick={this.handleSubmit2}/>;
    }

    return (
        <Container fluid="true">
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
                {currentForm}

            </Row>
        </Container>
    );
  }
}

export default Subscribe
