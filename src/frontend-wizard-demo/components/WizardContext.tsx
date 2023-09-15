import * as React from 'react';
import {useContext} from "react";

export interface WizardContextType {
  isStepCompleted: boolean;
  completeStep: () => void;
  markStepAsIncomplete: () => void;
  canMoveToNextStep: () => void;
}

export const WizardContext = React.createContext<WizardContextType | undefined>({
  isStepCompleted: false,
  completeStep: () => {
  },
  canMoveToNextStep: () => {
  },
  markStepAsIncomplete: () => {
  },
});

export const useWizardContext = (): WizardContextType => {
  const context = useContext<WizardContextType>(WizardContext);
  if (!context) {
    throw new Error('useWizardContext must be used within a WizardContext.Provider');
  }
  return context;
};

