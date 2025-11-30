# API Structure

Этот проект использует классовую структуру для работы с API.

## Архитектура

```
api/
├── base/
│   └── BaseApi.ts          # Базовый класс для всех API
├── SessionsApi.ts          # API для работы с сессиями
├── types.ts                # Типы TypeScript
├── index.ts                # Экспорты
└── README.md               # Эта документация
```

## Базовый класс BaseApi

`BaseApi` - абстрактный класс, который предоставляет:

- Методы для HTTP запросов: `get`, `post`, `put`, `delete`, `patch`
- Управление заголовками
- Обработку ошибок
- Построение URL

Все API классы должны наследоваться от `BaseApi`.

## Пример: SessionsApi

```typescript
import { SessionsApi } from '~/api'

const sessionsApi = new SessionsApi('http://localhost:8000')

// Создать сессию
const session = await sessionsApi.createSession({
  language: 'javascript',
  code: 'console.log("Hello")'
})

// Получить сессию
const session = await sessionsApi.getSession('session-id')

// Обновить код
await sessionsApi.updateCode('session-id', { code: 'new code' })

// Обновить язык
await sessionsApi.updateLanguage('session-id', { language: 'python' })
```

## Использование в компонентах

### Способ 1: Через composable (рекомендуется)

```typescript
// В компоненте Vue
<script setup lang="ts">
const api = useApi()

// Использовать wrapper методы (обратная совместимость)
const session = await api.createSession('javascript', 'code')

// ИЛИ использовать классы напрямую
const session = await api.sessions.createSession({
  language: 'javascript',
  code: 'code'
})
</script>
```

### Способ 2: Прямое создание экземпляра

```typescript
<script setup lang="ts">
import { SessionsApi } from '~/api'

const config = useRuntimeConfig()
const sessionsApi = new SessionsApi(config.public.apiBase)

const session = await sessionsApi.getSession('id')
</script>
```

## Создание нового API класса

Для добавления нового типа API (например, для пользователей):

1. Создайте новый файл `api/UsersApi.ts`:

```typescript
import { BaseApi } from './base/BaseApi'
import type { User } from './types'

export class UsersApi extends BaseApi {
  private readonly basePath = '/api/users'

  async getUser(userId: string): Promise<User> {
    return this.get<User>(`${this.basePath}/${userId}`)
  }

  async createUser(data: CreateUserRequest): Promise<User> {
    return this.post<User>(this.basePath, data)
  }
}
```

2. Добавьте типы в `api/types.ts`:

```typescript
export interface User {
  id: string
  name: string
  email: string
}

export interface CreateUserRequest {
  name: string
  email: string
}
```

3. Экспортируйте в `api/index.ts`:

```typescript
export { UsersApi } from './UsersApi'
```

4. Добавьте в `composables/useApi.ts`:

```typescript
export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const sessionsApi = new SessionsApi(apiBase)
  const usersApi = new UsersApi(apiBase)

  return {
    sessions: sessionsApi,
    users: usersApi,
    // ... остальные методы
  }
}
```

## Преимущества такой структуры

1. **Типизация** - полная поддержка TypeScript
2. **Переиспользование** - BaseApi содержит всю общую логику
3. **Масштабируемость** - легко добавлять новые API классы
4. **Тестируемость** - классы легко мокировать и тестировать
5. **Разделение ответственности** - каждый класс отвечает за свою область
6. **Единообразие** - все API работают одинаково

## Обработка ошибок

Все ошибки автоматически обрабатываются в `BaseApi.handleError()`:

```typescript
try {
  await api.sessions.getSession('invalid-id')
} catch (error: ApiError) {
  console.error(error.message)
  console.error(error.code)
  console.error(error.details)
}
```

## Кастомизация заголовков

```typescript
// В BaseApi можно переопределить defaultHeaders
class SessionsApi extends BaseApi {
  constructor(baseURL: string) {
    super(baseURL)
    this.defaultHeaders = {
      ...this.defaultHeaders,
      'X-Custom-Header': 'value'
    }
  }
}

// Или передать заголовки в конкретный запрос
await this.get('/path', {
  headers: { 'Authorization': 'Bearer token' }
})
```
