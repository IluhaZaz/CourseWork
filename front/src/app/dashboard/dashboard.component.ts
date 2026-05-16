import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';      
import { FormsModule } from '@angular/forms';       
import { ToDoItem, TodoService } from '../todo_service/todo.service';
import { AuthService } from '../auth_service/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  todos: ToDoItem[] = [];
  newTodoTitle = '';
  newTodoPriority = 1; 
  newTodoDoTill: string | null = null;
  newTodoComment: string | null = null;
  isLoading = true;

  constructor(
    private todoService: TodoService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTodos();
  }

  loadTodos(): void {
    this.isLoading = true;
    this.todoService.getTodos().subscribe({
      next: (todos) => {
        this.todos = todos;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  addTodo(): void {
    if (!this.newTodoTitle.trim()) return;

    const newTodo: ToDoItem = {
      id: ``,
      name: this.newTodoTitle.trim(),
      is_done: false,
      comment: this.newTodoComment?.trim() || null,
      priority: this.newTodoPriority,    
      do_till: this.newTodoDoTill ? new Date(this.newTodoDoTill) : null
    };

    this.todoService.addTodo(newTodo).subscribe({
      next: () => {
        this.newTodoTitle = '';
        this.newTodoComment = '';
        this.newTodoDoTill = null;
        this.loadTodos();
      }
    });
  }

  toggleTodo(todo: ToDoItem): void {
    todo.is_done = !todo.is_done;
    this.todoService.markasdoneTodo(todo.id).subscribe();
  }

  deleteTodo(id: string): void {
    this.todoService.deleteTodo(id).subscribe({
      next: () => {
        this.loadTodos();
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getTodosByPriority(priority: number): ToDoItem[] {
    return this.todos.filter(todo => todo.priority === priority);
  }

  autoGrow(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = '${textarea.scrollHeight}px';
  }

}
