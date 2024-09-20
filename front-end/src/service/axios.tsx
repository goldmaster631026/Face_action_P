import axios from 'axios'

const port = 5000
const api = axios.create({
    baseURL:`http://172.174.177.117:${port}/api`
    // baseURL:`https://10.1.0.4:${port}/api`
    // timeout : 5000
})

export default api