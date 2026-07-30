import { configureStore } from '@reduxjs/toolkit'
import complaintReducer from './features/complaintSlice'
import formReducer from './features/formSlice'
import copilotReducer from './features/copilotSlice'

export const store = configureStore({
  reducer: {
    complaints: complaintReducer,
    form: formReducer,
    copilot: copilotReducer,
  },
})