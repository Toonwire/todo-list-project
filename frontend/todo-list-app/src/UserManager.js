import React from 'react';
import axios from 'axios';
import './UserManager.css';
import { Link } from "react-router-dom";


class UserManager extends React.Component {
   
    constructor(props) {
        super(props);

        this.state = {
            users: [],
            newUser: {
                username: "",
                firstName: "",
                lastName: "",
                role_desc: "",
            },
            availableRoles: [],
        }
    }

    componentDidMount() {
        this.fetchUsers();
        this.getAvailableUserRoles();
    }

    fetchUsers = () => {
        console.log("fetching users");
        const headers = {
            'Content-Type': 'application/json'
        };

        axios.get('http://localhost:5000/users', {}, {headers: headers, withCredentials: true}).then(res => {
            console.log(res)
            const resUser = res.data.users;
            console.log(resUser);

            this.setState({users: resUser});

        }).catch(err => {
            console.log(err)
        })
    }

    deleteUser(userId) {
        console.log("deleting user with id: " + userId);
        const headers = {
            'Content-Type': 'application/json'
        };

        axios.delete('http://localhost:5000/user', {
            data: {
                user_id: userId
            }
        }, {headers: headers, withCredentials: true}).then(res => {
            console.log(res);
            this.fetchUsers();
        }).catch(err => {
            console.log(err);
        })
    }

    handleUsernameChange = (e) => {
        let updatedUser = this.state.newUser;
        updatedUser.username = e.target.value;
        this.setState({newUser: updatedUser})
    }
    handleFirstNameChange = (e) => {
        let updatedUser = this.state.newUser;
        updatedUser.firstName = e.target.value;
        this.setState({newUser: updatedUser})
    }
    handleLastNameChange = (e) => {
        let updatedUser = this.state.newUser;
        updatedUser.lastName = e.target.value;
        this.setState({newUser: updatedUser})
    }
    handleRoleDescChange = (e) => {
        let updatedUser = this.state.newUser;
        updatedUser.role_desc = e.target.value;
        this.setState({newUser: updatedUser})
    }

    generateTempPassword(len=8) {
        const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
        let pw = "";
        for (var i = 0, n = possible.length; i < len; ++i) {
            pw += possible.charAt(Math.floor(Math.random() * n));
        }
        return pw;
    }
    
    addUser = (e) => {
        e.preventDefault(); // no page reload

        const tempPass = this.generateTempPassword(8);
        console.log(tempPass);
        const headers = {
            'Content-Type': 'application/json'
        };

        axios.post('http://localhost:5000/user', {
            username: this.state.newUser.username,
            first_name: this.state.newUser.firstName,
            last_name: this.state.newUser.lastName,
            password: tempPass,
            confirm_password: tempPass,
            role_desc: this.state.newUser.role_desc
        }, {headers: headers, withCredentials: true}).then(res => {
            this.setState({newUser: {
                username: "",
                firstName: "",
                lastName: "",
                role_desc: this.state.newUser.role_desc,
            }}, () => {
                this.fetchUsers();
            });
        }).catch(err => {
            console.log(err);
        })
    }

    getAvailableUserRoles() {
        const headers = {
            'Content-Type': 'application/json'
        };
        axios.get('http://localhost:5000/roles', {}, {headers: headers, withCredentials: true}).then(res => {
            this.setState({
                availableRoles: res.data.roles
            });
        }).catch(err => {
            console.log(err);
        })
    }

    render() {
        const userListItems = this.state.users.map(user => 
            <div className="tr" key={user.id}>
                <span className="td">{user.username}</span>
                <span className="td">{user.first_name}</span>
                <span className="td">{user.last_name}</span>
                <span className="td">{user.role_desc}</span>
                {user.id !== this.props.userId ? <span className="td"><button onClick={() => this.deleteUser(user.id)}>delete user</button></span> : null}
            </div>
        );

        const userRoles = this.state.availableRoles.map(role => 
            <option key={role} value={role}>{role}</option>
        ); 
        console.log(userRoles);

        return (
            <div>
                <h3><Link to="/todolists">Back to todolists</Link></h3>
                <div id="tab-user" className="table">
                    <div className="th">	
                        <span className="td">Username</span>
                        <span className="td">First name</span>
                        <span className="td">Last name</span>
                        <span className="td">Role</span>
                    </div>
                    {userListItems}
                    <form className="tr" onSubmit={this.addUser}>
                        <span className="td"><input required type="text" value={this.state.newUser.username} onChange={this.handleUsernameChange}/></span>
                        <span className="td"><input required type="text" value={this.state.newUser.firstName} onChange={this.handleFirstNameChange}/></span>
                        <span className="td"><input required type="text" value={this.state.newUser.lastName} onChange={this.handleLastNameChange}/></span>
                        <span className="td">
                            <select defaultValue={this.state.newUser.role_desc} onChange={this.handleRoleDescChange} required>
                                <option value="" disabled>--role--</option>
                                {userRoles}
                            </select>
                        </span>
                        <span className="td"><input id="btn_submit_adduser" type="submit" name="submit" value="add user"/></span>
                    </form>
                </div>
                
            </div>
		);
    }
}

export default UserManager;