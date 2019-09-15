import React, { Component } from 'react';
import PrivacyPolicy from './pdf/Chirping_Canary_Privacy_Policy.pdf';
//import TermsConditions from './pdf/Chirping_Canary_Terms_Conditions.pdf';
import CookiePolicy from './pdf/Chirping_Canary_Cookie_Policy.pdf';
import { Col, Row, Container} from 'reactstrap';
import CookieConsent from "react-cookie-consent";

function Link(props) {
  return (
    <a href = {props.link} target = "_blank" rel="noopener noreferrer">{props.linkText}</a>
  );
}

class Footer extends Component {
  render() {

    let privacyPolicy
    let cookiePolicy
    let imageAttributionFreePik
    let imageAttributionFlatIcon
    //let termsConditions
    //let cookiePolicy

    privacyPolicy = <Link link={PrivacyPolicy} linkText="Privacy Policy"/>
    cookiePolicy = <Link link={CookiePolicy} linkText="Cookie Policy"/>
    imageAttributionFreePik = <Link link="https://www.freepik.com/" linkText="Freepik"/>
    imageAttributionFlatIcon = <Link link="www.flaticon.com/" linkText="www.flaticon.com"/>
    //termsConditions = <PDF pdf={TermsConditions} pdfName="Terms & Conditions"/>
    //cookiePolicy = <PDF pdf={CookiePolicy} pdfName="Cookie Policy"/>

    return (
      <Container fluid="true">
          <Row className="mt-1">
              <Col className="flex-xs-middle">
                {privacyPolicy} | {cookiePolicy}
              </Col>
          </Row>
          <Row className="mt-1">
            <Col className="flex-xs-middle">
              <p><font size="1">Chirping Canary Icon made by {imageAttributionFreePik} from {imageAttributionFlatIcon}</font></p>
            </Col>
          </Row>
          <CookieConsent buttonText="Ok ">
            This website uses cookies to enhance your user experience. Read more in the Chirping Canary {cookiePolicy} and {privacyPolicy}.
            If you continue to use this site we will assume that you are happy with this.
          </CookieConsent>
      </Container>

    );
  }
}

export default Footer
