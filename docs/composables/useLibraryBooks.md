# useLibraryBooks

## Purpose
Library book management composable handling book catalog, borrowing, returning, and library administration.

## Location
`frontend/composable/useLibraryBooks.js`

## State Management

### Reactive State
```javascript
const books = ref([])           // Book catalog
const borrowedBooks = ref([])  // User's borrowed books
const availableBooks = ref([]) // Available books
const bookDetails = ref(null)  // Selected book details
const loading = ref(false)     // Loading state
const borrowing = ref(false)   // Borrowing operation state
```

### Book Data Structure
```javascript
interface Book {
  name: string           // Book ID
  title: string          // Book title
  author: string         // Author name
  isbn: string           // ISBN number
  publisher: string      // Publisher
  publication_year: number // Publication year
  category: string       // Book category
  subject: string        // Subject area
  description: string    // Book description
  total_copies: number   // Total copies available
  available_copies: number // Currently available
  location: string       // Shelf location
  book_image: string     // Cover image URL
  status: 'Available' | 'Borrowed' | 'Reserved' | 'Damaged'
}
```

### Borrowing Record Structure
```javascript
interface BorrowingRecord {
  name: string           // Record ID
  book: string          // Book ID
  book_title: string    // Book title
  student: string       // Borrower ID
  borrowed_on: string   // Borrow date
  due_date: string      // Return due date
  returned_on?: string  // Actual return date
  status: 'Active' | 'Returned' | 'Overdue'
  fine_amount?: number  // Outstanding fine
  renewed_count: number // Renewal count
}
```

## API Methods

### fetchBooks(filters)
Retrieves book catalog with filters.

**Parameters:**
```javascript
{
  title?: string        // Search by title
  author?: string       // Search by author
  category?: string     // Filter by category
  subject?: string      // Filter by subject
  status?: string       // Filter by availability
  isbn?: string         // Search by ISBN
}
```

**Returns:** Promise<Book[]>

### getBookDetails(bookId)
Retrieves detailed book information.

**Parameters:**
```javascript
string  // Book ID
```

**Returns:** Promise<Book>

### borrowBook(bookId, data)
Borrows a book for user.

**Parameters:**
```javascript
string, {
  expected_return?: string  // Expected return date
  remarks?: string         // Borrowing remarks
}
```

**Returns:** Promise<BorrowingRecord>

### returnBook(borrowingId, data)
Returns a borrowed book.

**Parameters:**
```javascript
string, {
  condition?: 'Good' | 'Damaged'  // Book condition
  remarks?: string               // Return remarks
}
```

**Returns:** Promise<BorrowingRecord>

### renewBook(borrowingId)
Renews borrowing period.

**Parameters:**
```javascript
string  // Borrowing record ID
```

**Returns:** Promise<BorrowingRecord>

### getBorrowedBooks(userId)
Retrieves user's borrowed books.

**Parameters:**
```javascript
string?  // User ID (optional, defaults to current user)
```

**Returns:** Promise<BorrowingRecord[]>

### searchBooks(query)
Performs full-text search on books.

**Parameters:**
```javascript
string  // Search query
```

**Returns:** Promise<Book[]>

### reserveBook(bookId)
Reserves a book when unavailable.

**Parameters:**
```javascript
string  // Book ID
```

**Returns:** Promise<Reservation>

### getBookHistory(bookId)
Gets borrowing history for a book.

**Parameters:**
```javascript
string  // Book ID
```

**Returns:** Promise<BorrowingRecord[]>

## Usage Examples

### Book Catalog Search
```javascript
const { books, loading } = useLibraryBooks()

const searchBooks = async (query) => {
  loading.value = true
  try {
    const results = await fetchBooks({
      title: query,
      status: 'Available'
    })
    books.value = results
  } finally {
    loading.value = false
  }
}

// Template
<div v-for="book in books" :key="book.name">
  <img :src="book.book_image" alt="Cover" />
  <h3>{{ book.title }}</h3>
  <p>By {{ book.author }}</p>
  <p>{{ book.available_copies }}/{{ book.total_copies }} available</p>
  <button @click="borrowBook(book.name)" :disabled="book.available_copies === 0">
    Borrow
  </button>
</div>
```

### Borrowing a Book
```javascript
const { borrowBook, borrowing } = useLibraryBooks()

const handleBorrow = async (bookId) => {
  try {
    borrowing.value = true
    const record = await borrowBook(bookId, {
      expected_return: '2024-02-15', // 2 weeks from now
      remarks: 'For project research'
    })
    showToast(`Book borrowed! Due: ${record.due_date}`)
    // Refresh borrowed books list
    await getBorrowedBooks()
  } catch (err) {
    showError('Borrowing failed')
  } finally {
    borrowing.value = false
  }
}
```

### User's Borrowed Books
```javascript
const { borrowedBooks } = useLibraryBooks()

// Load on mount
onMounted(async () => {
  const books = await getBorrowedBooks(user.value.name)
  borrowedBooks.value = books
})

// Template
<div v-for="record in borrowedBooks" :key="record.name">
  <h4>{{ record.book_title }}</h4>
  <p>Due: {{ record.due_date }}</p>
  <p :class="record.status === 'Overdue' ? 'overdue' : ''">
    Status: {{ record.status }}
  </p>
  <button @click="returnBook(record.name)">Return</button>
  <button @click="renewBook(record.name)">Renew</button>
</div>
```

### Book Details View
```javascript
const { bookDetails } = useLibraryBooks()

const loadBookDetails = async (bookId) => {
  const details = await getBookDetails(bookId)
  bookDetails.value = details
}

// Template
<div v-if="bookDetails">
  <img :src="bookDetails.book_image" class="book-cover" />
  <div class="book-info">
    <h2>{{ bookDetails.title }}</h2>
    <p>Author: {{ bookDetails.author }}</p>
    <p>ISBN: {{ bookDetails.isbn }}</p>
    <p>Category: {{ bookDetails.category }}</p>
    <p>Available: {{ bookDetails.available_copies }}/{{ bookDetails.total_copies }}</p>
    <p>Location: {{ bookDetails.location }}</p>
    <p>{{ bookDetails.description }}</p>
  </div>
</div>
```

## Features

### Book Catalog Management
- Full-text search capabilities
- Category and subject filtering
- Availability status tracking
- Book cover image support

### Borrowing System
- Due date management
- Renewal functionality
- Fine calculation for overdue books
- Borrowing history tracking

### Reservation System
- Book reservation when unavailable
- Reservation queue management
- Notification system for available books

### Administrative Features
- Book condition tracking on return
- Damage reporting
- Borrowing statistics
- Inventory management

## Dependencies
- useFrappeFetch for API calls
- useAuth for user permissions
- Date utilities for due date calculations

## Business Rules
- Maximum borrowing period (2 weeks default)
- Maximum books per user (5 default)
- Fine calculation for overdue books
- Reservation holds for 24 hours
- Damaged book reporting required

## Error Cases
- Book not available
- Borrowing limit exceeded
- Overdue books blocking new borrows
- Invalid book conditions
- Reservation conflicts