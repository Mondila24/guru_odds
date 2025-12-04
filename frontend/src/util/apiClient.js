import axios from 'axios'

const baseURL = process.env.REACT_APP_API_BASE_URL || 'https://guru-odds.onrender.com'

const api = axios.create({ baseURL })

export default api
