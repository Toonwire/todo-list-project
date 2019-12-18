import React from 'react';
import axios from 'axios';
import './Login.css';

import "react-router-dom";


class Login extends React.Component {
   
    constructor(props) {
        super(props)

        this.state = {
            userId: null,
            userRole: null,
            username: "",
            password: "",
            loginFailed: false,
            // loginToken: this.props.loginToken,
        }
        
    }

    componentDidMount(){
        // try to login automatically (ie. cookie-based)
        console.log("try auto login");
        this.handleLogin(null);
    }

    handleLogin = (event) => {
        var cookieLogin = false;
        try {
            event.preventDefault();
        } catch (err) {
            console.log("No login event detected - attempt login via cookie");
            cookieLogin = true;
        }

        const username = this.state.username;
        const password = this.state.password;
        
        const headers = {
            'Content-Type': 'application/json'
        }
        axios.post('http://localhost:5000/login', {
            username: username,
            password: password,
        }, {headers: headers, withCredentials: true}).then(res => {
            console.log(res);
            const verifiedUser = res.data.user;
            this.setState({
                userId: verifiedUser.id,
                userRole: verifiedUser.role_desc,
            }, () => {
                this.props.onLoginSuccess(verifiedUser);
            });
        }).catch(err => {
            console.log(err.response);
            this.setState({loginFailed: !cookieLogin});
        });
    }

    handleUsernameChange = (e) => {
        this.setState({username: e.target.value, loginFailed: false});
    }

    handlePasswordChange = (e) => {
        this.setState({password: e.target.value, loginFailed: false});
    }

    render() {

        return (
			<form className="login-form" onSubmit={this.handleLogin}>
				<h1>Login</h1>
	
				<p>Username:</p>
				<input type="text" required maxLength="40" size="20" placeholder="" onChange={this.handleUsernameChange}/>
				<p>Password:</p>
				<input type="password" required maxLength="80" size="20" placeholder="" onChange={this.handlePasswordChange}/>
				<br/>
                
				<input id="btn_submit" type="submit" name="submit"/>
                <div className="form-response">
                    {(this.state.loginFailed ? "Incorrect username or password" : "") }
                </div>
			</form>
		);
    }
}

export default Login;