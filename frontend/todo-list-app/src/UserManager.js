import React from 'react';
import axios from 'axios';
import './UserManager.css';
import { Link } from "react-router-dom";


class UserManager extends React.Component {
   
    constructor(props) {
        super(props)


        this.state = {
            users: [],
        }
    }

    componentDidMount() {
        this.fetchUsers();
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

    render() {
        const userListItems = this.state.users.map(user => 
            <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.first_name}</td>
                <td>{user.last_name}</td>
                <td>{user.role_desc}</td>
            </tr>
        );
        return (
            <table id="tab_user">
                <thead>
                    <tr>	
                        <th>Username</th>
                        <th>First name</th>
                        <th>Last name</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
                    {userListItems}
                </tbody>
            </table>
		);
    }
}

export default UserManager;