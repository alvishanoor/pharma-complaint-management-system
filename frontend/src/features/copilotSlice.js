import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'
import { setFields } from './formSlice'

const API_BASE = 'http://localhost:8000'

export const sendCopilotMessage = createAsyncThunk(
  'copilot/sendMessage',
  async (message, { getState, dispatch, rejectWithValue }) => {
    try {
      const currentForm = getState().form.fields
      const response = await axios.post(`${API_BASE}/copilot/message`, {
        message,
        current_form: currentForm,
      })

      const { reply, ...fields } = response.data
      dispatch(setFields(fields))

      return { userMessage: message, reply }
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Copilot request failed')
    }
  }
)

export const uploadCopilotDocument = createAsyncThunk(
  'copilot/uploadDocument',
  async (file, { getState, dispatch, rejectWithValue }) => {
    try {
      const currentForm = getState().form.fields
      const formData = new FormData()
      formData.append('file', file)
      formData.append('current_form', JSON.stringify(currentForm))

      const response = await axios.post(`${API_BASE}/copilot/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      const { reply, ...fields } = response.data
      dispatch(setFields(fields))

      return { fileName: file.name, reply }
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'File upload failed')
    }
  }
)

const copilotSlice = createSlice({
  name: 'copilot',
  initialState: {
    messages: [
      {
        role: 'assistant',
        text: "Hi! Paste a complaint, or upload a document/image (PDF, email text, or photo), and I'll fill the form for you. You can also ask me to change any field afterwards.",
      },
    ],
    status: 'idle',
    error: null,
  },
  reducers: {
    resetChat(state) {
      state.messages = [
        {
          role: 'assistant',
          text: "Hi! Paste a complaint, or upload a document/image (PDF, email text, or photo), and I'll fill the form for you. You can also ask me to change any field afterwards.",
        },
      ]
      state.status = 'idle'
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendCopilotMessage.pending, (state, action) => {
        state.status = 'loading'
        state.error = null
        state.messages.push({ role: 'user', text: action.meta.arg })
      })
      .addCase(sendCopilotMessage.fulfilled, (state, action) => {
        state.status = 'idle'
        state.messages.push({ role: 'assistant', text: action.payload.reply })
      })
      .addCase(sendCopilotMessage.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload
        state.messages.push({ role: 'assistant', text: `Sorry, something went wrong: ${action.payload}` })
      })
      .addCase(uploadCopilotDocument.pending, (state, action) => {
        state.status = 'loading'
        state.error = null
        state.messages.push({ role: 'user', text: `Uploaded: ${action.meta.arg.name}` })
      })
      .addCase(uploadCopilotDocument.fulfilled, (state, action) => {
        state.status = 'idle'
        state.messages.push({ role: 'assistant', text: action.payload.reply })
      })
      .addCase(uploadCopilotDocument.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload
        state.messages.push({ role: 'assistant', text: `Sorry, couldn't read that file: ${action.payload}` })
      })
  },
})

export const { resetChat } = copilotSlice.actions
export default copilotSlice.reducer
