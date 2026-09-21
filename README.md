# TripEasy

TripEasy is a responsive group travel-planning web application. A trip Organiser can create a trip, add itinerary activities, invite other travellers via a shareable link, and track shared costs. Members can view the itinerary, respond to activities (Going / Maybe / Not Going), and see accommodation details — all in one place instead of scattered across group chats.

## Features

- **Authentication** — registration and login with JWT-based auth and bcrypt password hashing
- **Trips** — create, view, edit, and delete trips
- **Membership** — role-based access control (Organiser, Co-organiser, Member), shareable invite links, member removal
- **Itinerary** — add and view activities, RSVP tracking per activity
- **Accommodation** — add and view accommodation details for a trip
- **Costs** — running total of activity costs for a trip
- **AI packing list** — trip-specific packing suggestions generated via the Google Gemini API, using live trip data (destination, dates, activities) as context

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, JWT (python-jose), bcrypt (passlib)
**Frontend:** React (Vite), React Router
**AI:** Google Gemini API
**Tools:** Git, GitHub, pgAdmin, Swagger/OpenAPI (auto-generated API docs)

## Project Status

Core backend (auth, trips, membership, itinerary, accommodation, costs, AI packing list) and core frontend (login, register, dashboard, trip detail, itinerary with RSVP, accommodation, members) are complete and functional. Next: styling polish, testing, and deployment.

## Planning Documents

Requirements, ER diagram, use case diagram, and wireframes are available in `/docs`.
