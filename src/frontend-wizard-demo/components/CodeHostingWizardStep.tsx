import * as React from 'react';
import {useEffect, useState} from 'react';
import {FormGroup, FormControlLabel, Switch, Checkbox, Divider} from '@mui/material';
import {useWizardContext} from "./WizardContext";

const CodeHostingWizardStep: React.FC = () => {
  const {canMoveToNextStep} = useWizardContext();

  const [publishToGithub, setPublishToGithub] = useState(false);
  const [codeSpaces, setCodeSpaces] = useState(false);
  const [githubPages, setGithubPages] = useState(false);
  const [githubActions, setGithubActions] = useState(false);

  useEffect(() => {
    canMoveToNextStep();
  }, [canMoveToNextStep]);

  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', padding: '20px'}}>

      <FormGroup style={{width: '300px', marginBottom: '20px'}}>
        <FormControlLabel
          control={
            <Switch
              checked={publishToGithub}
              onChange={() => setPublishToGithub(!publishToGithub)}
            />
          }
          label="Publish to GitHub"
        />

        <Divider style={{margin: '10px 0'}}/>

        <FormControlLabel
          control={
            <Checkbox
              checked={codeSpaces}
              onChange={() => setCodeSpaces(!codeSpaces)}
              disabled={!publishToGithub}
            />
          }
          label="Include Code Spaces"
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={githubPages}
              onChange={() => setGithubPages(!githubPages)}
              disabled={!publishToGithub}
            />
          }
          label="Include GitHub Pages Support"
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={githubActions}
              onChange={() => setGithubActions(!githubActions)}
              disabled={!publishToGithub}
            />
          }
          label="Include GitHub Actions"
        />
      </FormGroup>
    </div>
  );
};

export default CodeHostingWizardStep;
