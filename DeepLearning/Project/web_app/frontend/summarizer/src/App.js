import Main from "./components/main"; 
import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes
} from "react-router-dom";

function App() {
  return (
    <div className="App" style = {{minHeight: "100%"}}>
      <Router>
        <Routes>
          <Route exact path="/" element={<Main />}/>
        </Routes>
      </Router>
    </div>
  );
}

export default App;