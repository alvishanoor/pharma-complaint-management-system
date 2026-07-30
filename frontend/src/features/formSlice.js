import { createSlice } from '@reduxjs/toolkit'

const initialForm = {
  customer_name: '',
  product_name: '',
  batch_number: '',
 
  country: '',
  quantity_affected: '',
  complaint_text: '',
  attachment_filename: '',
}

const formSlice = createSlice({
  name: 'form',
  initialState: {
    fields: { ...initialForm },
  },
  reducers: {
    updateField(state, action) {
      const { name, value } = action.payload
      state.fields[name] = value
    },
    setFields(state, action) {
      state.fields = { ...state.fields, ...action.payload }
    },
    resetForm(state) {
      state.fields = { ...initialForm }
    },
  },
})

export const { updateField, setFields, resetForm } = formSlice.actions
export default formSlice.reducer
