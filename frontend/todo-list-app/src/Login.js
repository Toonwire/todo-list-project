import React from 'react';
import axios from 'axios';
import './Login.css';

import { withRouter } from "react-router-dom";


class Login extends React.Component {
   
    constructor(props) {
        super(props)

        this.state = {
            username: "",
            password: "",
            loginToken: this.props.loginToken,
        }
    }

    componentDidMount(){
        if (this.props.location.state && this.props.location.state.loginToken) // check if there is a redirect state 
            this.setState({loginToken: this.props.location.state.loginToken}, () => {
                console.log(this.state.loginToken);
                this.handleLoginWithToken();
            });
    }

    handleLoginWithToken = () => {
        const token = this.state.loginToken;

        const headers = {
            'Content-Type': 'application/json'
        }
        axios.post('http://localhost:5000/login/token', {
            login_token: token,
        }, {headers: headers}).then(res => {
            console.log(res)
            if (res.data.statusCode === 200) {
                const verifiedUser = res.data.user;
                console.log(verifiedUser)
                this.props.onLoginSuccess(verifiedUser);
            } else {
                console.log('token did not exist');
            }
        })
    }

    handleLogin = (event) => {
        event.preventDefault();
        const username = this.state.username;
        const password = this.state.password;
        
        const headers = {
            'Content-Type': 'application/json'
        }
        axios.post('http://localhost:5000/login', {
            username: username,
            password: password,
        }, {headers: headers}).then(res => {
            console.log(res)
            if (res.data.statusCode === 200) {
                const verifiedUser = res.data.user;
                console.log(verifiedUser)
                this.setState({loginToken: verifiedUser.loginToken}, () => {
                    this.props.onLoginSuccess(verifiedUser);
                });
            }
        })
        
    }

    handleUsernameChange = (e) => {
        this.setState({username: e.target.value})
    }

    handlePasswordChange = (e) => {
        this.setState({password: e.target.value})
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
			</form>
		);
    }
}

export default withRouter(Login);