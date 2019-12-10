import React from 'react';
import './Checkbox.css'


class Checkbox extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            isChecked: this.props.isChecked,
        }
    }

    toggleChange = () => {
        this.props.onCheckChange();
    }

    render() {
        return (
            <div className="checkbox">
                <label>
                    <input type="checkbox"
                        checked={this.state.isChecked}
                        onChange={this.toggleChange}
                    />
                    {this.props.label}
                </label>
            </div>
        );
    }
}

export default Checkbox;