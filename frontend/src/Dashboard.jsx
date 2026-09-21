import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function Dashboard() {
  const [trips, setTrips] = useState([])

  useEffect(() => {
    async function fetchTrips() {
      const token = localStorage.getItem("token")

      const response = await fetch("http://localhost:8000/trips", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()
      setTrips(data)
    }

    fetchTrips()
  }, [])

  return (
    <div className="page">
      <h1>Your Trips</h1>

      <Link to="/create-trip" className="link-btn">+ Create a trip</Link>

      {trips.map(trip => (
        <Link to={`/trips/${trip.trip_id}`} key={trip.trip_id} style={{ textDecoration: "none" }}>
          <div className="card">
            <h3>{trip.name}</h3>
            <p>{trip.start_date} to {trip.end_date}</p>
          </div>
        </Link>
      ))}
    </div>
  )
}

export default Dashboard