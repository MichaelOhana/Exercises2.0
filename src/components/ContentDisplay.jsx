import React from 'react';
import LessonTemplate from './templates/LessonTemplate';
import ExerciseTemplate from './templates/ExerciseTemplate';
import QuizTemplate from './templates/QuizTemplate';
import styles from './ContentDisplay.module.css';

const ContentDisplay = ({ content, isMenuOpen }) => {
  const renderContent = () => {
    if (!content) {
      return <div className={styles.placeholder}>Select a lesson to begin</div>;
    }

    switch (content.type) {
      case 'lesson':
        return <LessonTemplate lesson={content} />;
      case 'exercise':
        return <ExerciseTemplate exercise={content} />;
      case 'quiz':
        return <QuizTemplate quiz={content} />;
      default:
        return <div>Content type not supported</div>;
    }
  };

  return (
    <div className={`${styles.contentDisplay} ${!isMenuOpen ? styles.expanded : ''}`}>
      {renderContent()}
    </div>
  );
};

export default ContentDisplay; 