import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

function JoinTrip() {
  const { inviteCode } = useParams()
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState("")

  useEffect(() => {
    async function joinTrip() {
      const token = localStorage.getItem("token")

      const response = await fetch(`http://localhost:8000/trips/join/${inviteCode}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (!response.ok) {
        setErrorMessage(data.detail)
        return
      }

      //success - redirect to the trip they just joined
      navigate(`/trips/${data.trip_id}`)
    }

    joinTrip()
  }, [inviteCode])

  if (errorMessage) {
    return <p style={{ color: "red" }}>{errorMessage}</p>
  }

  return <p>Joining trip...</p>
}

export default JoinTrip