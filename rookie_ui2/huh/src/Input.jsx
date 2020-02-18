
var React = require('react');
import {ControlLabel, FormControl} from 'react-bootstrap';



export default class Input extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      value: this.props.q,
    };
  }

  handleChange(e) {
    let v = e.target.value;
    this.setState({
      value: v
    });
    this.props.changeHandler(v);
  }

  render() {
    let qstyle = {
      fontWeight: "bold",
      color: "#0028a3"
    };
    return (
      <FormControl
        type="text"
        style={qstyle}
        value={this.state.value}
        placeholder="Enter text"
        ref="input"
        groupclassame="group-class"
        labelclassname="label-class"
        onChange={this.handleChange} />
    );
  }

}
