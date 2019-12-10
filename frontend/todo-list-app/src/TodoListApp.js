import React from 'react';
import './TodoListApp.css';
import axios from 'axios';
import TodoList from './TodoList';
import Login from './Login';
import Register from './Register';
import {
	BrowserRouter as Router,
	Switch,
	Route,
	Link,
	Redirect
  } from "react-router-dom";



class TodoListApp extends React.Component {

	constructor(props) {
		super(props);


		this.state = {
			user: {
				id: null,
				username: "",
				// loginToken: "",
			},
			todoListTabs: [],
			newTabLabel: "",
		}
	}

	getUserTodoLists() {	
		// call backend to init todolists
		axios.get('http://localhost:5000/todolists', {
			params: {
				user_id: this.state.user.id
			}
		}).then(res => {
				console.log(res)
				let initTodoListTabs = []
				const todoLists = res.data['todo_lists'] // [{..},{..}, ..]
				todoLists.forEach(todoList => {
					const listId = todoList['id'] 
					const title = todoList['title']
					const todoItems = todoList['todo_items']
					const jsxTodoList = <TodoList key={listId} id={listId} todos={todoItems} filter={"filter-all"} onTodoListChange={this.onTodoListChange}/>
					initTodoListTabs.push({id: listId, label: title, isActive: false, todoList: jsxTodoList})
				});

				initTodoListTabs[0]['isActive'] = true
				this.setState({todoListTabs: initTodoListTabs})
			}).catch(err => {
				console.log(err.response);
			})
	}


	onTodoListChange = (tabId, todos, filter) => {
		// update todolist references to reflect changes
        const tabs = this.state.todoListTabs;
        let changedTab = tabs.find(tab => {
            return tab.id === tabId
        })
		const updatedTodoList = <TodoList key={tabId} id={tabId} todos={todos} filter={filter} onTodoListChange={this.onTodoListChange} />
		changedTab.todoList = updatedTodoList;
		
        this.setState({todoListTabs: tabs});

	}

	setActive(todoListTabIndex) {
		let todoListTabs = this.state.todoListTabs;
		todoListTabs[todoListTabIndex].isActive = true;
		for (let [index, todoListTab] of todoListTabs.entries()) {
			if (index !== todoListTabIndex) todoListTab.isActive = false;
		}
		this.setState(todoListTabs);
	} 

	renderTodoListTabs = () => {
		return this.state.todoListTabs.map((todoListTab, index) => {
			return (
				<div key={index} className={'todo-list-tab ' + (todoListTab.isActive ? 'active' : 'inactive')}>
					<button className='todo-list-tab' onClick={() => this.setActive(index)}>
						{todoListTab.label}
					</button>
				</div>
			);
		})
	}
	
	ActiveTodoList (props) {
		const tabs = props.todoListTabs;
		if (tabs.length === 0) return (<span>No todos loaded</span>)
		var activeTab = tabs.find(function(tab) {
			return tab.isActive;
		});

		return activeTab.todoList;
	}

	handleCreateNewTodoList = () => {
		let tabs = this.state.todoListTabs;
		const newTabTitle = this.state.newTabLabel

		if (newTabTitle.trim().length === 0) {
			console.log("cannot insert empty todo list");
			return;
		}

		axios.post('http://localhost:5000/todolist', {
			title: newTabTitle.trim(),
			user_id: this.state.user.id
		}).then(res => {
			console.log(res)
			// response > data > todo_list carries inserted todolist object (json)
			if (res.status === 200) {

				const todoList = res.data.todo_list;
				const newTab = {
					id: todoList.id,
					label: todoList.title,
					isActive: false,
					todoList: <TodoList key={todoList.id} id={todoList.id} todos={[]} filter={"filter-all"} onTodoListChange={this.onTodoListChange}/>,
				}

				tabs.push(newTab);
				this.setState({todoListTabs: tabs, newTabLabel: ""});
			}
		});		
	}

    handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            this.handleCreateNewTodoList();
        }
    }
    
    onNewTabChange = (e) => {
		this.setState({newTabLabel: e.target.value});
	}
	
	onLoginSuccess = (user) => {
		// user: {id, username, login_token}
		const loggedInUser = {
			id: user.id,
			username: user.username,
			// loginToken: user.login_token,
		}
		console.log(user.id);
		this.setState({user: loggedInUser}, this.getUserTodoLists);
	}

	
	render() {  
		const isUserLoggedIn = this.state.user.id !== null;
		console.log("Is user logged in: " + isUserLoggedIn);

		return (
			<Router>			
				<Switch>
					<Route 
						path="/todolists"
						render = {() =>
							isUserLoggedIn ?
							<div className="todo-list-app">
								<div>
									<input className="todo-list-new" type="text" placeholder="New todo list" value={this.state.newTabLabel} onChange={this.onNewTabChange} onKeyDown={this.handleKeyDown} />
								</div>
								<div className="todo-list-tabs">
									{this.renderTodoListTabs()}
								</div>
								<this.ActiveTodoList todoListTabs={this.state.todoListTabs}/>
							</div>
							: <Redirect to='/login' />
						} 
					/>
					<Route 
						path="/login"
						render = {() =>
							isUserLoggedIn ? <Redirect to='/todolists'/> : <Login onLoginSuccess={this.onLoginSuccess}/>
						}
					/>
					<Route exact path="/register">
						<Register />
					</Route>
					<Route exact path="/">
						<div>
							<h3>Please <Link to="/login">log in</Link> to use the service</h3>
						</div>
					</Route>
				</Switch>
			</Router>	
		);
	}
}



// ========================================

export default TodoListApp;