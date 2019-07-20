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
                <Label for="code" sm={2}>Verification Code</Label>
                <Col sm={6}>
                    <Input id="code" name="code" type="text" placeholder=""/>
                </Col>
            </FormGroup>
            <Col sm={6}>
            <Button color="danger" align='right'>Confirm Subscription</Button>
            </Col>
        </Form>
    </Col>
  );
};


function SubscriptionConfirmed(props) {
  return (
    <Col>
        <p>
        Congratulations you have registered for Chirping Canary.
        </p>
    </Col>
  );
};



function CurrentError(props) {
  return (
    <Col>
        <p>
        {props.errorMessage}
        </p>
    </Col>
  );
};

class Subscribe extends Component {

  constructor() {
    super();
    this.handleSubmitSubscribe = this.handleSubmitSubscribe.bind(this);
    this.handleSubmitConfirmSubscription = this.handleSubmitConfirmSubscription.bind(this);
    this.state = {
      flow: 'home',
      phone: '',
      currentError: ''
    };
  };

  handleSubmitSubscribe(event) {

    event.preventDefault();
    const data = new FormData(event.target);

    fetch('/api/subscribe', {
      method: 'POST',
      body: data,
    })
    .then(response => {
      if (response.status === 200) {
        this.setState({phone: data.get('phone')})
        this.setState({flow: "confirm_subscription"})
        this.setState({currentError: ''})
      } else {
        response.json()
        .then(data => this.setState({currentError: data.message}))
      }
    });
  };

  handleSubmitConfirmSubscription(event) {

    event.preventDefault();
    const data = new FormData(event.target);
    data.append('phone', this.state.phone);

    fetch('/api/subscribe/verify', {
      method: 'POST',
      body: data,
    })
    .then(response => {
      if (response.status === 200) {
        this.setState({flow: "subscription_confirmed"})
        this.setState({currentError: ''})
      } else {
        response.json()
        .then(data => this.setState({currentError: data.message}))
      }
    });
  };

  render() {

    const flow = this.state.flow
    let currentForm

    if (flow == 'home') {
      currentForm = <Home onClick={this.handleSubmitSubscribe}/>;
    } else if (flow === 'confirm_subscription')  {
      currentForm = <ConfirmSubscription onClick={this.handleSubmitConfirmSubscription}/>;
    } else if (flow === 'subscription_confirmed') {
      currentForm = <SubscriptionConfirmed/>
    }

    let currentErrorMessage
    currentErrorMessage = <CurrentError errorMessage={this.state.currentError}/>;

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
                {currentErrorMessage}
            </Row>
        </Container>
    );
  }
}

export default Subscribe
