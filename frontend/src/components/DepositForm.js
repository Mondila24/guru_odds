import React, { useState } from 'react';
import '../css/DepositForm.css';
// Axios
import api from "../util/apiClient";

import { useSelector, useDispatch } from 'react-redux';

// Redux
import { initializeBalance } from '../slices/userSlice';
import { Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const DepositForm = ({ onClose, currentBalance }) => {
      // Custom styled button for the Deposit
    const InvalidButton = styled(Button)(({ theme }) => ({
        marginRight: theme.spacing(2),
        backgroundColor: '#fc0202',
        '&:hover': {
        backgroundColor: '#0056b3', // a bit darker on hover
        }
    }));
  const [depositAmount, setDepositAmount] = useState(0);
  // user authentication selectors
  const authToken = useSelector((state) => state.auth.token);
  const balance = useSelector((state) => state.user.balance);

  const dispatch = useDispatch()

  const handleDeposit = (e) => {
    e.preventDefault();
    // Ensure depositAmount is a positive number or zero
    const deposit = parseFloat(depositAmount);
    if (isNaN(deposit) || deposit < 0) {
      alert("Invalid deposit amount. Please enter a positive number or zero.");
      return;
    }

    api({
        method: "POST",
        url:"/api/payments/initiate",
        headers: {
            Authorization: 'Bearer ' + authToken,
          },
        data:{
          amount: deposit
         }
      })
      .then((response) => {
        const url = response.data.data?.authorization_url || response.data.authorization_url
        if (url) {
          window.open(url, '_blank')
        }
        onClose()
      }).catch((error) => {
        if (error.response) {
          }
      })
  };

  return (
    <div className="popup-container">
      <div className="popup">
        <p>Current Balance: ${currentBalance}</p>
        <form onSubmit={handleDeposit}>
          <label style={{ textAlign: 'center' }}>
            Deposit Amount:
            <input
              type="number"
              step="0.01"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              min="1"  // Prevent negative values
            />
          </label>
          <div style={{ textAlign: 'center' }}>
          <button type="submit">Deposit</button>
          </div>
        </form>
        <p>Expected Balance: ${depositAmount === "" ? currentBalance : (Number(currentBalance) + parseFloat(depositAmount)).toFixed(2)}</p>
        <div style={{ textAlign: 'center' }}>
        <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default DepositForm;

