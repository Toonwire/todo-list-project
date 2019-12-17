import React from 'react';
import './TodoList.css';
import axios from 'axios';
import {SortableContainer, SortableElement} from 'react-sortable-hoc';
import arrayMove from 'array-move';
import TodoItem from './TodoItem';



class TodoList extends React.Component {
    
    constructor(props) {
        super(props);

        this.state = {
            todos: this.props.todos,
            newTodo: {
                id: 0,
                label: "",
                completed: false,
                dueDate: null,
                priority: 0,
            },
            filter: this.props.filter,
        }
    }

    handleNewTodoChange = (e) => {
        let updatedTodo = this.state.newTodo;
        updatedTodo.label = e.target.value;
        updatedTodo.id = this.state.todos.length;
        this.setState({newTodo: updatedTodo});
    }

    handleCreateTodo = e => {
        const newTodo = this.state.newTodo;
        const todoListId = this.props.id;

        if (newTodo.label.trim().length > 0) {

            axios.post('http://localhost:5000/todo', {
                label: newTodo.label.trim(),
                completed: newTodo.completed,
                due_date: newTodo.dueDate,
                priority: this.state.todos.length+1,
                todolist_id: todoListId,
            }).then(res => {
                console.log(res)

                const insertedTodo = res.data.todo;
                const todo = {
                    id: insertedTodo.id,
                    label: insertedTodo.label,
                    completed: insertedTodo.completed,
                    due_date: insertedTodo.due_date,
                    priority: insertedTodo.priority,
                }

                let allTodos = this.state.todos;
                allTodos.push(todo);
                this.setState({todos: allTodos, newTodo: {id: 0, label: "", completed: false, dueDate: null}});
                this.handleTodoListChange();
            })
        } else {
            console.log("cannot insert empty todo");
        }
    }

    handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            this.handleCreateTodo();
        }
    }


    updateTodo = (todoId, isCompleted, dueDate) => {   
        let todos = this.state.todos;
        let todo = todos.find(todo => {
            return todo.id === todoId;
        });

        // const newCompleted = isCompleted === null ? todo.completed : isCompleted;
        // const newDueDate = dueDate === null ? todo.due_date : dueDate;
        
        var utcDate = dueDate === null ? null : new Date(dueDate).toISOString().slice(0, 19).replace('T', ' '); // yyyy-mm-dd HH:MM:SS

        axios.patch('http://localhost:5000/todo', {
            id: todo.id,
            completed: isCompleted,
            due_date: utcDate,
            priority: todo.priority
        }).then(res => {
            console.log(res)
            const resTodo = res.data.todo;

            // var localDate = new Date(resTodo.due_date);
            // localDate.setHours(localDate.getHours(), localDate.getMinutes() - new Date().getTimezoneOffset(), localDate.getSeconds());  // account for timezone offset

            const updatedTodo = {
                id: resTodo.id,
                label: resTodo.label,
                completed: resTodo.completed,
                dueDate: resTodo.due_date,
                priority: resTodo.priority
            }
            
            // const priorityList = props.todoItems;
            // priorityList.sort(function(t1, t2) {
            //     return t1.priority - t2.priority;
            // });

            todo.completed = updatedTodo.completed;
            todo.due_date = updatedTodo.dueDate;
            this.setState({todos: todos}, () => {
                this.handleTodoListChange();
            });
        })
    }

    handleTodoListChange = () => {
        this.props.onTodoListChange(this.props.id, this.state.todos, this.state.filter);
    }

    activeTodos = () => {
        const activeItems = [];
        this.state.todos.forEach(todo => {
            if (!todo.completed) activeItems.push(todo);
        });
        // return this.state.todos.filter(todo => !todo.completed).length;
        return activeItems.length;
    }

    changeTodoFilter = (e) => {
        const filterType = e.target.id;
        this.setState({filter: filterType}, () => {
            this.handleTodoListChange();
        });
    }

    clearCompletedTodos = () => {
        const activeTodos = this.state.todos.filter(todo => !todo.completed);
        const todoListId = this.props.id;

        axios.patch('http://localhost:5000/todos/completed', {
            todolist_id: todoListId
        }).then(res => {
            console.log(res);
            this.setState({todos: activeTodos}, () => {
                this.handleTodoListChange();
            });
        })
    }

    
    onSortEnd = ({oldIndex, newIndex}) => {
        // deep copy todos and rearrange array to match drag/drop
        let priorityTodos = JSON.parse(JSON.stringify(this.state.todos));
        priorityTodos = arrayMove(priorityTodos, oldIndex, newIndex);

        // remap priorities of each todo
        priorityTodos.map((todo, index) => todo.priority = index+1);
        this.setState({
            todos: priorityTodos
        }, () => {
            // this.state.todos.map(todo => this.updateTodo(todo.id, todo.completed, todo.due_date));  
            this.state.todos.forEach(todo => this.updateTodo(todo.id, todo.completed, todo.due_date));  // expensive API consumation but it's okay for now
        });
    }

    // arraySwap = (arr, from, to) => {
    //     let swapped = JSON.parse(JSON.stringify(arr));
    //     let tempFrom = JSON.parse(JSON.stringify(swapped[from]));
    //     let tempTo = JSON.parse(JSON.stringify(swapped[to]));
    //     swapped[from] = tempTo;
    //     swapped[to] = tempFrom;
    //     return swapped;
    // }



    render() { 
        
        const SortableTodoContainer = SortableElement((props) => {
            return (
                <TodoItem key={props.todo.id} id={props.todo.id} label={props.todo.label} completed={props.todo.completed} dueDate={props.todo.due_date} priority={props.todo.priority} onTodoChange={props.onTodoChange}/>
            )
        });

        const TodoContainer = SortableContainer((props) => {
            const listItems = props.todoItems.map((todo, index) => <SortableTodoContainer 
                                                                        key={todo.id} 
                                                                        index={index} 
                                                                        todo={todo}
                                                                        onTodoChange={this.updateTodo} />);
            const filter = props.filter;
            const filteredItems = listItems.filter((item) => filter === "filter-all" || (filter === "filter-active" && !item.props.todo.completed) || (filter === "filter-completed" && item.props.todo.completed));
            
            return (
                <div className="todo-items">
                    <ul>
                        {filteredItems}
                    </ul>
                </div>
            );
        });

        return (
            <div className="content-wrapper">
                <input className="todo-item-new" type="text" placeholder="What needs to be done?.." value={this.state.newTodo.label} onChange={this.handleNewTodoChange} onKeyDown={this.handleKeyDown}/>
                <div className="todo-list">
                    <TodoContainer todoItems={this.state.todos} filter={this.state.filter} onSortEnd={this.onSortEnd} pressDelay={100} />
                </div>          
                <div className="footer">
                    <div className="row">
                        <label className="column">{this.activeTodos()} items left</label>
                        <div className="column">
                            <div>
                                <button id="filter-all" type="button" className={'btn-filter-' + (this.state.filter === "filter-all" ? "active" : "inactive")} onClick={this.changeTodoFilter}>All</button>
                                <button id="filter-active" type="button" className={'btn-filter-' + (this.state.filter === "filter-active" ? "active" : "inactive")} onClick={this.changeTodoFilter}>Ongoing</button>
                                <button id="filter-completed" type="button" className={'btn-filter-' + (this.state.filter === "filter-completed" ? "active" : "inactive")} onClick={this.changeTodoFilter}>Completed</button>
                            </div>                        
                        </div>
                        <button type="button" id="btn_clear_completed" className="column" onClick={this.clearCompletedTodos}>Clear completed</button>
                    </div>
                </div>
            </div>
        )
    }
}
export default TodoList;
