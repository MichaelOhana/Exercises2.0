import React from 'react';
import styles from './Templates.module.css';

const QuizTemplate = ({ quiz }) => {
  return (
    <div className={styles.template}>
      <h1>{quiz.title}</h1>
      <div className={styles.content}>
        <section>
          <h2>Question 1</h2>
          <div>
            <label>
              <input type="radio" name="q1" value="a" /> Option A
            </label>
            <label>
              <input type="radio" name="q1" value="b" /> Option B
            </label>
            <label>
              <input type="radio" name="q1" value="c" /> Option C
            </label>
          </div>
        </section>
      </div>
      
      <button className={styles.nextButton}>Submit Quiz</button>
    </div>
  );
};

export default QuizTemplate; 