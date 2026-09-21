import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import AddActivityForm from './AddActivityForm'
import AddAccommodationForm from './AddAccommodationForm'

function TripDetail() {
  const { tripId } = useParams()
  const [trip, setTrip] = useState(null)
  const [activities, setActivities] = useState([])
  const [responses, setResponses] = useState({})
  const [accommodations, setAccommodations] = useState([])
  const [members, setMembers] = useState([])
  const [currentUserId, setCurrentUserId] = useState(null)
  const [totalCost, setTotalCost] = useState(0)
  const [packingList, setPackingList] = useState("")

  useEffect(() => {
    async function fetchTrip() {
      const token = localStorage.getItem("token")

      const response = await fetch(`http://localhost:8000/trips/${tripId}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()
      setTrip(data)
    }

    fetchTrip()
  }, [tripId])

  useEffect(() => {
    async function fetchActivities() {
      const token = localStorage.getItem("token")

      const response = await fetch(`http://localhost:8000/trips/${tripId}/activities`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()
      setActivities(data)
    }

    fetchActivities()
  }, [tripId])

  useEffect(() => {
    async function fetchAccommodations() {
      const token = localStorage.getItem("token")

      const response = await fetch(`http://localhost:8000/trips/${tripId}/accommodation`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()
      setAccommodations(data)
    }

    fetchAccommodations()
  }, [tripId])

  useEffect(() => {
  async function fetchMembers() {
    const token = localStorage.getItem("token")

    const response = await fetch(`http://localhost:8000/trips/${tripId}/members`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })

    const data = await response.json()
    setMembers(data)
  }

  fetchMembers()
}, [tripId])

useEffect(() => {
  async function fetchCurrentUser() {
    const token = localStorage.getItem("token")

    const response = await fetch("http://localhost:8000/me", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })

    const data = await response.json()
    setCurrentUserId(data.user_id)
  }

  fetchCurrentUser()
}, [])

  useEffect(() => {
    async function fetchCosts() {
      const token = localStorage.getItem("token")

      const response = await fetch(`http://localhost:8000/trips/${tripId}/costs`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()
      setTotalCost(data.total_cost)
    }

    fetchCosts()
  }, [tripId])

  useEffect(() => {
  async function fetchPackingList() {
    const token = localStorage.getItem("token")

    const response = await fetch(`http://localhost:8000/trips/${tripId}/packing-list`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })

    const data = await response.json()
    setPackingList(data.packing_list)
  }

  fetchPackingList()
}, [tripId])

async function handleRemoveMember(userId) {
  const token = localStorage.getItem("token")

  await fetch(`http://localhost:8000/trips/${tripId}/members/${userId}`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })

  //refresh the members list so the removed person disappears immediately
  //filter it to all members from memberhip that dont have that user id
  setMembers(prevMembers => prevMembers.filter(membership => membership.user.user_id !== userId))
}


  // handleRespond takes parameters because there's no single state variable
  // that could represent "which activity" or "which status" - there are
  // multiple activity cards on screen at once, each with 3 buttons.
  async function handleRespond(activityId, status) {
    const token = localStorage.getItem("token")

    await fetch(`http://localhost:8000/trips/${tripId}/activities/${activityId}/respond`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ status: status })
    })



    //needed to declare setResponses as we arent just replacing data but we are keeping the old and adding the new
    //...prevResponses  says take every key-value pair currently inside prevResponses
    // and copy them all into this new object.
   setResponses(prevResponses => ({
      ...prevResponses,
      [activityId]: status
    }))
  }

  if (!trip) {
    return <p>Loading...</p>
  }

  //Go through every membership in the list,
  // and find the ONE where the member's user_id matches the currently logged-in user's ID
  //all to find yourself
  const myMembership = members.find(membership => membership.user.user_id === currentUserId)
  //if my myMembership exists and the role is organiser
const isOrganiser = myMembership && myMembership.role === "Organiser"

  return (
    <div>
      <h1>{trip.name}</h1>
      <p>{trip.start_date} to {trip.end_date}</p>

      <h2>Itinerary</h2>
      
      <AddActivityForm
  tripId={tripId}
  onActivityAdded={(newActivity) => setActivities(prev => [...prev, newActivity])}
/>

      {activities.map(activity => (
        <div key={activity.activity_id}>
          <h3>{activity.name}</h3>
          <p>{activity.date} — {activity.start_time} - {activity.end_time}</p>
          <p>{activity.address}</p>

          <button
          //onclick it adds the response using setResponse then style checks if the response was this then do...
            onClick={() => handleRespond(activity.activity_id, "Going")}
            style={{ fontWeight: responses[activity.activity_id] === "Going" ? "bold" : "normal" }}
          >
            Going
          </button>
          <button
            onClick={() => handleRespond(activity.activity_id, "Maybe")}
            style={{ fontWeight: responses[activity.activity_id] === "Maybe" ? "bold" : "normal" }}
          >
            Maybe
          </button>
          <button
            onClick={() => handleRespond(activity.activity_id, "Not Going")}
            style={{ fontWeight: responses[activity.activity_id] === "Not Going" ? "bold" : "normal" }}
          >
            Not Going
          </button>
        </div>
      ))}

<p>Total cost of activities so far: €{totalCost}</p>

{/*tells the browser "respect the actual line breaks in this text," 
so the packing list displays across multiple lines*/}
<h2>Packing List</h2>
<p style={{ whiteSpace: "pre-line" }}>{packingList}</p>

      <h2>Accommodation</h2>
{accommodations.map(accommodation => (
  <div key={accommodation.accommodation_id}>
    <h3>{accommodation.address}</h3>
    <p>{accommodation.check_in_date} to {accommodation.check_out_date}</p>
  </div>
))}

<AddAccommodationForm
  tripId={tripId}
  onAccommodationAdded={(newAccommodation) => setAccommodations(prev => [...prev, newAccommodation])}
/>

 <h2>Members</h2>
{members.map(membership => (
  <div key={membership.membership_id}>
    <p>{membership.user.name} — {membership.role}</p>
    {/* Remove button only shows if BOTH are true:
    1. I am the Organiser (isOrganiser)
    2. This specific row isn't the Organiser's own row (membership.role !== "Organiser") */}
     {isOrganiser && membership.role !== "Organiser" && (
      <button onClick={() => handleRemoveMember(membership.user.user_id)}>
        Remove
      </button>
    )}
  </div>
))}


           
    </div>
  )
}

export default TripDetail