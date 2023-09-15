import * as React from 'react';
import {useState} from 'react';
import {Box, Button, Container, Step, StepLabel, Stepper} from '@mui/material';
import {WizardContext} from "./WizardContext";
import LanguageWizardStep from "./LanguageWizardStep";
import FrameworkWizardStep from "./FrameworkWizardStep";
import FeaturesWizardStep from "./FeaturesWizardStep";
import CodeHostingWizardStep from "./CodeHostingWizardStep";

enum WizardSteps {
  Language,
  Framework,
  Features,
  CodeHosting,
  Deployment
}

const stepLabels = [
  'Select language',
  'Select framework',
  'Choose features',
  'Code hosting',
  'Deployment',
]

const Wizard: React.FC = () => {
  const [activeStep, setActiveStep] = useState<WizardSteps>(WizardSteps.Language);
  const [isStepCompleted, setIsStepCompleted] = useState(false);

  const handleNext = () => {
    if (activeStep < WizardSteps.Deployment) {
      setActiveStep((prevStep) => prevStep + 1);
      setIsStepCompleted(false);
    }
  };

  const handleBack = () => {
    if (activeStep > WizardSteps.Language) {
      setActiveStep((prevStep) => prevStep - 1);
      setIsStepCompleted(false);
    }
  };

  const getStepContent = (step: WizardSteps) => {
    switch (step) {
      case WizardSteps.Language:
        return <LanguageWizardStep/>;
      case WizardSteps.Framework:
        return <FrameworkWizardStep/>;
      case WizardSteps.Features:
        return <FeaturesWizardStep/>;
      case WizardSteps.CodeHosting:
        return <CodeHostingWizardStep/>;
      default:
        return 'Unknown step';
    }
  };
  const handleLabelClick = (stepIndex) => {
    if (stepIndex <= activeStep) {
      setActiveStep(stepIndex);
    }
  };

  return (
    <Container>
      <Stepper activeStep={activeStep}>
        {stepLabels.map((label, index) => (
          <Step key={label}>
            <StepLabel
              onClick={() => handleLabelClick(index)}
              // Make it visually evident that it's clickable
              style={{
                cursor: index <= activeStep ? 'pointer' : 'default'
              }}
            >
              {label}
            </StepLabel>
          </Step>
        ))}
        {/*<Step><StepLabel>Select Language</StepLabel></Step>*/}
        {/*<Step><StepLabel>Select Framework</StepLabel></Step>*/}
        {/*<Step><StepLabel>Choose Features</StepLabel></Step>*/}
        {/*<Step><StepLabel>Code Hosting</StepLabel></Step>*/}
        {/*<Step><StepLabel>Deployment</StepLabel></Step>*/}
      </Stepper>

      <Box my={4}>
        <WizardContext.Provider value={{
          isStepCompleted,
          completeStep: () => {
            setIsStepCompleted(true);
            handleNext();
          },
          canMoveToNextStep: () => {
            setIsStepCompleted(true);
          },
          markStepAsIncomplete: () => setIsStepCompleted(false),
        }}>
          {getStepContent(activeStep)}
        </WizardContext.Provider>
      </Box>

      <Box display="flex" justifyContent="flex-end" mt={4}>
        {activeStep !== WizardSteps.Language && (
          <Button color="primary" onClick={handleBack} style={{marginRight: '8px'}}>Back</Button>
        )}
        <Button
          variant="contained"
          color="primary"
          disabled={!isStepCompleted}
          onClick={handleNext}
        >
          {activeStep === WizardSteps.Deployment ? 'Finish' : 'Next'}
        </Button>
      </Box>
    </Container>
  );
}

export default Wizard;
