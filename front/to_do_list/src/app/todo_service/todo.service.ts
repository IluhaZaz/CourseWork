import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../enviroment';
import { map, Observable } from 'rxjs';

export interface ToDoItem {
  id: string;
  name: string;
  comment: string | null;
  priority: number;
  is_done: boolean;
  do_till: Date | null;
}

interface ApiResponse {
  status: string;
  detail: string;
  data: ToDoItem[];
}

@Injectable({
  providedIn: 'root'
})
export class TodoService {
  private apiUrl = `${environment.apiUrl}/todo`;

  constructor(private http: HttpClient) {}

  getTodos(): Observable<ToDoItem[]> {
    return this.http.get<ApiResponse>(`${this.apiUrl}/get_items`).pipe(
      map(response => response.data)
    );
  }

  addTodo(todo: ToDoItem): Observable<ToDoItem> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/add_item`, todo).pipe(
      map(response => response.data[0])
    );
  }

  updateTodo(todo: ToDoItem): Observable<ToDoItem> {
    return this.http.patch<ApiResponse>(`${this.apiUrl}/update_item?item_id=${todo.id}`, todo).pipe(
      map(response => response.data[0])
    );
  }

  markasdoneTodo(id: string): Observable<ToDoItem> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/toggle_status?item_id=${id}`, ``).pipe(
      map(response => response.data[0])
    );
  }

  deleteTodo(id: string): Observable<void> {
    return this.http.delete<ApiResponse>(`${this.apiUrl}/delete_item?item_id=${id}`).pipe(
      map(() => {})
    );
  }
}