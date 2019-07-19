import React, { Component } from 'react';
import logo from './img/canary.png';
import { Col, Row, Container, Badge } from 'reactstrap';

const ColoredLine = ({ color }) => (
    <hr
        style={{
            color: color,
            backgroundColor: color,
            height: 50
        }}
    />
);

class Header extends Component {

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
        </Container>

    );
  }
}

export default Header
