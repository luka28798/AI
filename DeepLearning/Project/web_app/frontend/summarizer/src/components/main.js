import React, { Component } from "react";
import { NavLink } from 'react-router-dom'
import Summarize from "./summarize";
import 'bootstrap/dist/css/bootstrap.min.css';
import {
  Navbar,
  NavDropdown,
  Nav
  } from "react-bootstrap";

class Main extends Component {
  render() {
    return (
      <div style = {{backgroundColor: "B3E5FC", minHeight: "100%"}}>
          <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
            <div style = {{marginLeft: "15px"}}><Navbar.Brand><NavLink to="/" style = {{color: "#FBFBFB", textDecoration: 'none'}}>Text Summarizer</NavLink></Navbar.Brand></div>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
            </Navbar.Collapse>
          </Navbar>
      
        <div style={{display:"flex", width : "100%", height : "100%",justifyContent:"center", flexDirection:"row", padding:"20px", width:"auto", backgroundColor:"#B3E5FC"}}>
          
            <div style={{width:"100%", height: "100%"}}>
                <Summarize></Summarize>
            </div>
        </div>
        </div>
    );
  }
}

export default Main;