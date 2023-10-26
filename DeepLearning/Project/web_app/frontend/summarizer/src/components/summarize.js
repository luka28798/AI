import React, { Component} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import {
    Button,
    InputGroup,
    Form,
    ListGroup
  } from "react-bootstrap";
  
import axios from "axios";


class Summarize extends Component {
    constructor(props) {
        super(props);
        this.state = {
            text:"",
            summarized_text:""
        };
        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }


    onChange(e) {
        this.setState({ [e.target.name]: e.target.value })
      }
  
      onSubmit(e) {
        this.setState({summarized_text: ""})
          e.preventDefault()
          let data ={
              "text": this.state.text
          }
          axios.post(`/summarize`, data).then(res => {
            console.log(res, "summarized_text");
            this.setState({summarized_text: res.data})
                });
      }

  render() {
    return (
          <div style={{padding:"80px", background:"#B3E5FC", minHeight:"100%", width: "90%", marginLeft: "50px"}}>
            <div style = {{width:"45%", float : "Left", display: "block"}}>
            <h3 style={{margin:"auto", marginBottom:"20px"}}>Text:</h3>
            
            <InputGroup size="lg" style={{}}>
            <Form onSubmit={this.onSubmit} style={{width:"100%"}}>
                    <Form.Group >
                        <Form.Control 
                        style={{width:"100%", resize: "none", rows: 10, height: "200px"}}
                        size="lg"
                        as="textarea" 
                        placeholder="Enter text you want to summarize... " 
                        type="text"
                        name="text"
                        value={this.state.text}
                        onChange={this.onChange}
                        spellcheck = "false"
                        />
                        </Form.Group>
                        <div style = {{marginTop: "40px"}}><Button variant="primary" type="submit" style={{margin: "auto" , textAlign: "center", display: "flex", alignItems: "center", justifyContent : "center"}}>
                            Summarize it!
                        </Button>
                        </div>
                        
                </Form>
            </InputGroup>
            </div>
            <div style = {{width:"45%", float : "Left", display: "block"}}>
              <h3 style={{margin: "auto", marginBottom: "20px", marginLeft: "90px"}}>Summary:</h3>
              {this.state.summarized_text === "" ? 
              <div style={{marginLeft: "90px", width: "100%", display: "block",  float : "Left"}}>   
                <ListGroup style =  {{width : "100%"}}>
                  <ListGroup.Item variant="info" style = {{height : "200px"}} >
                    <p style={{margin:"0"}}></p>
                  </ListGroup.Item>
                </ListGroup>
              </div> : <div style={{marginLeft: "90px", width: "100%", display: "block",  float : "Left"}}>   
                <ListGroup style =  {{width : "100%"}}>
                  <ListGroup.Item variant="info" style = {{height : "200px"}} >
                    <p style={{margin:"0"}}>{this.state.summarized_text}</p>
                  </ListGroup.Item>
                </ListGroup>
              </div>}
            </div>
            
            
          </div>
    );
  }
}

export default Summarize;