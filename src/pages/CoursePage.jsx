import React, { useState } from 'react';
import CourseNavigation from '../components/CourseNavigation';
import ContentDisplay from '../components/ContentDisplay';
import styles from './CoursePage.module.css';

const CoursePage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(true);
  const [currentContent, setCurrentContent] = useState(null);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <div className={styles.coursePage}>
      <CourseNavigation 
        isOpen={isMenuOpen} 
        onToggle={toggleMenu}
        onContentSelect={setCurrentContent}
      />
      <ContentDisplay 
        content={currentContent}
        isMenuOpen={isMenuOpen}
      />
    </div>
  );
};

export default CoursePage; 