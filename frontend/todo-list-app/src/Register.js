import React from 'react';
import axios from 'axios';
import './Register.css';
import { Redirect } from "react-router-dom";


class Register extends React.Component {
   
    constructor(props) {
        super(props)


        this.state = {
            user: {
                username: "",
                firstName: "",
                lastName: "",            
                password: "",
                confirmPassword: "",
                id: null,
            },
        }
    }

    register = (event) => {
        event.preventDefault();

        const user = this.state.user;
        const headers = {
            'Content-Type': 'application/json'
        };

        axios.post('http://localhost:5000/user', {
            username: user.username,
            first_name: user.firstName,
            last_name: user.lastName,
            password: user.password,
            confirmPassword: user.confirmPassword,
        }, {headers: headers}).then(res => {
            console.log(res)
            if (res.data.statusCode === 200) {
                const resUser = res.data.user;
                console.log(resUser);

                const loggedInUser = this.state.user;
                loggedInUser.id = resUser.id;

                this.setState({user: loggedInUser});
            }
        }).catch(err => {
            console.log(err)
        })
        
    }

    handleUsernameChange = (e) => {
        const updatedUser = this.state.user;
        updatedUser.username = e.target.value;
        this.setState({user: updatedUser})
    }
    handleFirstNameChange = (e) => {
        const updatedUser = this.state.user;
        updatedUser.firstName = e.target.value;
        this.setState({user: updatedUser})
    }
    handleLastNameChange = (e) => {
        const updatedUser = this.state.user;
        updatedUser.lastName = e.target.value;
        this.setState({user: updatedUser})
    }
    handlePasswordChange = (e) => {
        const updatedUser = this.state.user;
        updatedUser.password = e.target.value;
        this.setState({user: updatedUser})
    }
    handleConfirmPasswordChange = (e) => {
        const updatedUser = this.state.user;
        updatedUser.confirmPassword = e.target.value;
        this.setState({user: updatedUser})
    }

    render() {
        if (this.state.user.loginToken)
            return (
                <Redirect to='/login' />
            )

        return (
			<form className={"register-form" + (this.state.user.loginToken ? " success" : "")} onSubmit={this.register}>
                <h1>
                    {(() => {
                        console.log('login-token: ' + this.state.user.loginToken)
                        if (this.state.user.loginToken) return "Success"
                        return "Register"
                    })()}

                </h1>
                
				<p>Username:</p>
				<input type="text" required maxLength="40" size="20" placeholder="" onChange={this.handleUsernameChange}/>
				<p>First name:</p>
				<input type="text" required maxLength="40" size="20" placeholder="" onChange={this.handleFirstNameChange}/>
				<p>Last name:</p>
				<input type="text" required maxLength="40" size="20" placeholder="" onChange={this.handleLastNameChange}/>
				<p>Password:</p>
				<input type="password" required maxLength="80" size="20" placeholder="" onChange={this.handlePasswordChange}/>
				<p>Confirm password:</p>
				<input type="password" required maxLength="80" size="20" placeholder="" onChange={this.handleConfirmPasswordChange}/>
				<br/>
                
				<input id="btn_submit" type="submit" name="submit"/>
			</form>
		);
    }
}

export default Register;