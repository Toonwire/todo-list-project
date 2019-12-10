import React from 'react';
import './TodoItem.css';
import Checkbox from './Checkbox';
// import img_deadline from './img/deadline_512px.png';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import 'react-datepicker/dist/react-datepicker-cssmodules.css'

class TodoItem extends React.Component {
    
    constructor(props) {
        super(props);

        const due = {
            OVERDUE: 'due-over',
            SOON: 'due-soon',
            MEDIUM: 'due-medium',
            LONG: 'due-long',
            NEVER: 'due-never',
        } 

        function whenDue(date) {
            if (props.dueDate === null) return due.NEVER;

            const diffDays = (new Date(date) - new Date()) / 1000/60/60/24;
            let dueState = due.NEVER;
            switch (true) {
                case diffDays < 0:
                    dueState = due.OVERDUE;
                    break;
                case diffDays < 7:
                    dueState = due.SOON;
                    break;
                case diffDays < 14:
                    dueState = due.MEDIUM;
                    break;
                case diffDays > 14:
                    dueState = due.LONG;
                    break;
                default:
                    break;   
            }
            return dueState;
        }

        this.state = {
            completed: this.props.completed,
            dueDate: this.props.dueDate,
            dueState: whenDue(this.props.dueDate),
        }

    }

    onTodoChange = (completed, date) => {
        this.setState({completed: completed, dueDate: date}, () => {
            this.props.onTodoChange(this, completed, date);
        })
    }

    handleCheckboxChange = () => {
        this.onTodoChange(!this.state.completed, this.state.dueDate);
    }

    handleDueDateChange = (date) => {
        this.onTodoChange(this.state.completed, date);
    }

    render() {
        return (
            <li>
                <div className={'todo-item ' + (this.state.completed ? 'completed ' : 'ongoing ' + this.state.dueState)}>
                    <Checkbox 
                        label={this.props.label}
                        isChecked={this.state.completed}
                        onCheckChange={this.handleCheckboxChange} />
                    <div className="deadline">
                        <label>Due:</label>
                        <DatePicker
                            selected={this.state.dueDate !== null ? new Date(this.state.dueDate) : ""}
                            placeholderText="Never"
                            onChange={date => this.handleDueDateChange(date)}
                            showTimeSelect
                            disabled={this.state.completed}
                            timeFormat="HH:mm"
                            timeIntervals={30}
                            timeCaption="time"
                            dateFormat="dd/MM-yy HH:mm"
                        />
                        {/* <button id="btn_edit_deadline"><img id="btn_edit_deadline_img" src={img_deadline}/>adasd</button>  */}
                    </div>
                </div>
            </li>
        );
    }
}

export default TodoItem;