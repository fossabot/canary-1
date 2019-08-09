import React, { Component } from 'react';
import PrivacyPolicy from './pdf/Chirping_Canary_Privacy_Policy.pdf';
//import TermsConditions from './pdf/Chirping_Canary_Terms_Conditions.pdf';
//import CookiePolicy from './pdf/Chirping_Canary_Cookie_Policy.pdf';
import { Col, Row, Container} from 'reactstrap';

function PDF(props) {
  return (
    <a href = {props.pdf} target = "_blank" rel="noopener noreferrer">{props.pdfName}</a>
  );
}

class Footer extends Component {
  render() {

    let privacyPolicy
    //let termsConditions
    //let cookiePolicy

    privacyPolicy = <PDF pdf={PrivacyPolicy} pdfName="Privacy Policy"/>
    //termsConditions = <PDF pdf={TermsConditions} pdfName="Terms & Conditions"/>
    //cookiePolicy = <PDF pdf={CookiePolicy} pdfName="Cookie Policy"/>

    return (
      <Container fluid="true">
          <Row className="mt-1">
              <Col className="flex-xs-middle">
                {privacyPolicy}
              </Col>
          </Row>
      </Container>
    );
  }
}

export default Footer
