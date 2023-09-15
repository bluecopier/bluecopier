
import * as React from 'react';
import { useState } from 'react';
import { Box, Card, CardActionArea, CardContent, Grid, Typography } from '@mui/material';
import { useWizardContext } from './WizardContext';

const frameworks = [
  { label: "Django DRF", icon: "https://www.django-rest-framework.org/img/logo.png" },
  { label: "Django Strawberry", icon: "https://static.djangoproject.com/img/logos/django-logo-positive.svg" },
  { label: "Flask", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" },
  { label: "FastAPI", icon: "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" }
];

const FrameworkWizardStep: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null);
  const { completeStep } = useWizardContext();

  const handleFrameworkSelection = (framework: string) => {
    setSelectedFramework(framework);
    completeStep();
  };

  return (
    <Grid container spacing={3}>
      {frameworks.map((framework) => (
        <Grid item xs={6} sm={3} key={framework.label}>
          <Card elevation={selectedFramework === framework.label ? 4 : 1}>
            <CardActionArea
              onClick={() => handleFrameworkSelection(framework.label)}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '140px' }}
            >
              <CardContent>
                <Box marginBottom={1}>
                  <img src={framework.icon} alt={framework.label} width={50} />
                </Box>
                <Typography variant="body1">
                  {framework.label}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default FrameworkWizardStep;
