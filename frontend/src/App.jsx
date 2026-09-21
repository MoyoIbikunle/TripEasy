import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm'
import Dashboard from './Dashboard'
import CreateTrip from './CreateTrip'
import TripDetail from './TripDetail'
import JoinTrip from './JoinTrip'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/create-trip" element={<CreateTrip />} />
        <Route path="/trips/:tripId" element={<TripDetail />} />
        <Route path="/join/:inviteCode" element={<JoinTrip />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App