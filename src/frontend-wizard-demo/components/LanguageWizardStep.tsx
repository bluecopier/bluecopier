import * as React from 'react';
import { useState } from 'react';
import { Box, Card, CardActionArea, CardContent, Grid, Typography } from '@mui/material';
import { useWizardContext } from './WizardContext';

const languages = [
  { label: "Python", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" },
  { label: "Java", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg" },
  { label: "TypeScript", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" },
  { label: "PHP", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-plain.svg" },
  { label: "Go", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg" },
  { label: "Ruby", icon: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg" },
];

const LanguageWizardStep: React.FC = () => {
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
  const { completeStep } = useWizardContext();

  const handleLanguageSelection = (language: string) => {
    setSelectedLanguage(language);
    completeStep();
  };

  return (
    <Grid container spacing={3}>
      {languages.map((language) => (
        <Grid item xs={4} sm={2} key={language.label}>
          <Card elevation={selectedLanguage === language.label ? 4 : 1}>
            <CardActionArea
              onClick={() => handleLanguageSelection(language.label)}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '140px' }}
            >
              <CardContent>
                <Box marginBottom={1}>
                  <img src={language.icon} alt={language.label} width={50} />
                </Box>
                <Typography variant="body1">
                  {language.label}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default LanguageWizardStep;
