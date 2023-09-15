import * as React from 'react';
import {
  Checkbox,
  FormControlLabel,
  FormGroup, TextField,
} from '@mui/material';
import {useWizardContext} from './WizardContext';
import {useEffect, useState} from "react";

const features = [
  {label: "Code linting via Ruff", name: "code_linting"},
  {label: "Code formatting via Black", name: "code_formatting"},
  {label: "Type checking via MyPy", name: "type_checking"},
  {label: "Unit-testing  via Pytest", name: "unit_testing"},
];

const FeaturesWizardStep: React.FC = () => {
  const {canMoveToNextStep} = useWizardContext();

  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (projectName.trim() === '') {
      setError('Project name is required');
      // Here, you might want to disable or prevent `canMoveToNextStep` based on your implementation
    } else {
      setError('');
      canMoveToNextStep();
    }
  }, [projectName]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <TextField
        label="Project Name"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
        error={!!error}
        helperText={error}
        style={{ marginBottom: '20px' }}
        autoFocus
      />

      <FormGroup>
        {features.map(({ label, name }) => (
          <FormControlLabel control={<Checkbox defaultChecked />}
                            style={{ display: 'flex', alignItems: 'flex-start' }}
                            label={label}
                            key={name}/>
        ))}
      </FormGroup>
    </div>
  );
};

export default FeaturesWizardStep;
