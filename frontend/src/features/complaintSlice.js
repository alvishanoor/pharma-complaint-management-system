import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

export const submitComplaint = createAsyncThunk(
  'complaints/submit',
  async (formData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE}/complaints`, formData)
      return response.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Submission failed')
    }
  }
)

export const fetchComplaints = createAsyncThunk(
  'complaints/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_BASE}/complaints`)
      return response.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch complaints')
    }
  }
)

const complaintSlice = createSlice({
  name: 'complaints',
  initialState: {
    list: [],
    latestResult: null,
    status: 'idle',
    error: null,
  },
  reducers: {
    clearLatestResult(state) {
      state.latestResult = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitComplaint.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(submitComplaint.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.latestResult = action.payload
        state.list.unshift(action.payload)
      })
      .addCase(submitComplaint.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.list = action.payload
      })
  },
})

export const { clearLatestResult } = complaintSlice.actions
export default complaintSlice.reducer