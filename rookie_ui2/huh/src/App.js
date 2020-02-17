import React, { Component} from "react";
import "./App.css";
import "./QueryBar.jsx";

class App extends Component{
  render(){
    return(
      <div className="App">
        <QueryBar/>
        <h1> Hello, World! </h1>
      </div>
    );
  }
}

export default App;
