import React, { Component } from 'react';
import { Col, Button, Form, FormGroup, Label, Input, Row, Container } from 'reactstrap';


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
                        <option value="yellow">Moderate Concern for Sensitive Groups</option>
                        <option value="amber">Unhealthy for Sensitive Groups</option>
                        <option value="red">Unhealthy for Everyone</option>
                    </Input>
                </Col>
            </FormGroup>
            <FormGroup row>
                <Col sm={12}>
                    <Input type="checkbox" name="opt-in" id="opt-in" align='right'/>
                    Yes, I would like Chirping Canary to send me marketing communications by SMS (text message)
                </Col>
            </FormGroup>
            <Col sm={6}>
            <Button color="danger" align='left'>Subscribe</Button>
            </Col>
        </Form>
    </Col>
  );
};


function Unsubscribe(props) {
  return (
    <Col>
        <Form onSubmit={props.onClick}>
            <FormGroup row>
                <Label for="phone" sm={2}>Phone</Label>
                <Col sm={6}>
                    <Input id="phone" name="phone" type="text" placeholder="07719143007"/>
                </Col>
            </FormGroup>
            <Col sm={6}>
            <Button color="secondary" align='right'>Unsubscribe</Button>
            </Col>
        </Form>
    </Col>
  );
};


function ComfirmUnsubscribe(props) {
  return (
    <Col>
        <Form onSubmit={props.onClick}>
            <FormGroup row>
                <p>A six digit verification code has been sent to {props.phone}, please enter it to unsubscribe.</p>
                <Label for="code">Verification Code</Label>
                <Col sm={6}>
                    <Input id="code" name="code" type="text" placeholder=""/>
                </Col>
            </FormGroup>
            <Col sm={6}>
            <Button color="secondary" align='right'>Confirm Unsubscription</Button>
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
                <p>A six digit verification code has been sent to {props.phone}, please enter it to complete your subscription</p>
                <Label for="code">Verification Code</Label>
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


function UnsubscribeConfirmed(props) {
  return (
    <Col>
        <p>
        You have succesfully unsubcribed from Chirping Canary.
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
    this.handleSubmitUnsubscribe = this.handleSubmitUnsubscribe.bind(this);
    this.clickUnsubscribe = this.clickUnsubscribe.bind(this);
    this.handleSubmitConfirmUnSubscribe = this.handleSubmitConfirmUnSubscribe.bind(this);
    this.state = {
      flow: 'home',
      phone: '',
      currentError: '',
      optIn: 'off'
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
        let optInState = Object.values(data).indexOf("opt-in")
        if (optInState > -1) {
            this.setState({optIn: "on"})
        };
        this.setState({currentError: ''})
      } else {
        response.json()
        .then(data => this.setState({currentError: data.message}))
      }
    });
  };

  handleSubmitUnsubscribe(event) {

    event.preventDefault();
    const data = new FormData(event.target);

    fetch('/api/unsubscribe', {
      method: 'POST',
      body: data,
    })
    .then(response => {
      if (response.status === 200) {
        this.setState({phone: data.get('phone')})
        this.setState({flow: "confirm_unsubscribe"})
        this.setState({currentError: ''})
      } else {
        response.json()
        .then(data => this.setState({currentError: data.message}))
      }
    });
  };

  clickUnsubscribe(event) {
    this.setState({flow: "unsubscribe"})
  }


  handleSubmitConfirmUnSubscribe(event) {

    event.preventDefault();
    const data = new FormData(event.target);
    data.append('phone', this.state.phone);

    fetch('/api/unsubscribe/verify', {
      method: 'POST',
      body: data,
    })
    .then(response => {
      if (response.status === 200) {
        this.setState({flow: "unsubscription_confirmed"})
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
    data.append('opt-in', this.state.optIn);

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

    if (flow === 'home') {
      currentForm = <Home onClick={this.handleSubmitSubscribe}/>;
    } else if (flow === 'confirm_subscription')  {
      currentForm = <ConfirmSubscription onClick={this.handleSubmitConfirmSubscription} phone={this.state.phone}/>;
    } else if (flow === 'subscription_confirmed') {
      currentForm = <SubscriptionConfirmed/>;
    } else if (flow === 'unsubscribe') {
      currentForm = <Unsubscribe onClick={this.handleSubmitUnsubscribe}/>;
    } else if (flow === 'confirm_unsubscribe') {
      currentForm = <ComfirmUnsubscribe onClick={this.handleSubmitConfirmUnSubscribe} phone={this.state.phone}/>;
    } else if (flow === 'unsubscription_confirmed') {
      currentForm = <UnsubscribeConfirmed/>;
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
                    <p>
                    Click here to <Button color="secondary" align='right' size="sm" onClick={this.clickUnsubscribe}>Unsubscribe</Button>
                    </p>
                </Col>
                <Col>
                {currentForm}
                {currentErrorMessage}
                </Col>
            </Row>
        </Container>
    );
  }
}

export default Subscribe
