# Books
Overview

This project is a web-based tool designed to help users manage their book collections and reading experiences. The application allows users to log in, track books they are currently reading, books they want to read, and books they have already read, while also giving them the ability to rate books. Users can search for books using the Google Books API, have a current favorite book that is displayed on their profile for other users to see, and explore their reading history through detailed statistics and calendar views. Each time a user marks a book as completed, a post is automatically generated for other users to see with star rating and date read.

Technologies Used
Backend: Python, Flask
Frontend: HTML, CSS, Javascript
Database: SQLite (via SQLAlchemy)
Frameworks: Flask for backend logic and routing, Flask-Login for user authentication, Chart.js for data visualization, AJAX for instant search functionality
External API: Google Books API for book data search

How It Works
User Authentication: Users can register, log in, and log out to securely manage their book lists and posts.
Book Management: Users can:
Add books to their reading lists (e.g., "Currently Reading", "To Be Read", "Read").
Rate books.
Set a favorite book.
Book Search: Users can search for books from the Google Books API and add them to their collection.
Posts: After finishing a book, users select a star rating. Then a post is automatically created for other users to view.
Reading Statistics: Users can view an overview of their reading habits, including total books read, average ratings, most-read author, and monthly reading trends.
Calendar View: A calendar is provided to display the days on which the user read a book.
Deployment URL:
https://booksproject-7ab7ee507009.herokuapp.com

Learning Journey

- What inspired you to create this project:
I’ve always loved reading, and I wanted to create a tool that would help keep track of books in a simple, but pretty, way. I thought it would be fun to build a web app that looks exactly the way I've always wished apps like Goodreads would look — clean and easy to use.
- What potential impact do you believe it could have on its intended users or the broader community:
I believe this project can help readers stay motivated and organized by providing an easy and enjoyable way to track their reading journey. It allows users to see their progress through fun features like the calendar while seeing what other people are also reading in real time.
- What new technology you learned:
The new language I used was JavaScript.I learned how to use it to handle dynamic features, such as creating charts for reading statistics and implementing instant search functionality. Working with Chart.js also introduced me to data visualization techniques.
- Why you chose the new technology:
I chose JavaScript and Chart.js because I wanted the application to be interactive and engaging. JavaScript allowed me to make the book search faster and more responsive, while Chart.js helped me visualize the user’s reading data in an easily understandable way. These technologies were essential for making the project more functional and user-friendly.
- Challenges you faced, and what you learned from the experience:
One of the biggest challenges I faced was integrating the Google Books API, ensuring that the book information was accurate and properly displayed. Another challenge was figuring out exactly what data needed to be passed from the flask routers to the HTML pages to make them display the data accurately and efficiently. Overcoming these challenges taught me a lot about working with APIs and it also helped me understand the importance of clear, efficient communication between the frontend and backend.




https://github.com/user-attachments/assets/13474a8c-392b-4393-b20e-70009cf9cb58

