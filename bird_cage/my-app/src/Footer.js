import React, { Component } from 'react';
import PrivacyPolicy from './pdf/Chirping_Canary_Privacy_Policy.pdf';
//import TermsConditions from './pdf/Chirping_Canary_Terms_Conditions.pdf';
//import CookiePolicy from './pdf/Chirping_Canary_Cookie_Policy.pdf';
import { Col, Row, Container} from 'reactstrap';

function Link(props) {
  return (
    <a href = {props.link} target = "_blank" rel="noopener noreferrer">{props.linkText}</a>
  );
}

class Footer extends Component {
  render() {

    let privacyPolicy
    let imageAttributionFreePik
    let imageAttributionFlatIcon
    //let termsConditions
    //let cookiePolicy

    privacyPolicy = <Link link={PrivacyPolicy} linkText="Privacy Policy"/>
    imageAttributionFreePik = <Link link="https://www.freepik.com/" linkText="Freepik"/>
    imageAttributionFlatIcon = <Link link="www.flaticon.com/" linkText="www.flaticon.com"/>
    //termsConditions = <PDF pdf={TermsConditions} pdfName="Terms & Conditions"/>
    //cookiePolicy = <PDF pdf={CookiePolicy} pdfName="Cookie Policy"/>

    return (
      <Container fluid="true">
          <Row className="mt-1">
              <Col className="flex-xs-middle">
                {privacyPolicy}
              </Col>
          </Row>
          <Row className="mt-1">
            <Col className="flex-xs-middle">
              <p><font size="1">Chirping Canary Icon made by {imageAttributionFreePik} from {imageAttributionFlatIcon}</font></p>
            </Col>
          </Row>
      </Container>
    );
  }
}

export default Footer
